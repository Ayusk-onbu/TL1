import bpy
import math
import bpy_extras

bl_info = {
    "name": "LevelEditor",
    "author": "Hamada Kazuya",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "LevelEditor",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

# オペレータ 頂点を伸ばす
class MYADDON_OT_stretch_vertex(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_stretch_vertex"
    bl_label = "頂点を伸ばす"
    bl_description = "頂点座標を引っ張って伸ばします"
    # リドゥ、アンドゥ可能オプション
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行した時に呼ばれるコールバック関数
    def execute(self, context):
        bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
        print("頂点を伸ばしました。")

        # オペレータの命令終了
        return {'FINISHED'}

# オペレータ ICO球生成
class MYADDON_OT_create_ico_sphere(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_create_object"
    bl_label = "ICO球生成"
    bl_description = "ICO球を生成します"
    bl_options = {'REGISTER', 'UNDO'}

    # メニューを実行した時に呼ばれる関数
    def execute(self, context):
        bpy.ops.mesh.primitive_ico_sphere_add()
        print("ICO球を生成しました。")

        return {'FINISHED'}

# オペレータ シーン出力
class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label  = "シーン出力"
    bl_description = "シーン情報をExportします"
    filename_ext = ".scene"
    
    def write_and_print(self, file, str):
        print(str)

        file.write(str)
        file.write("\n")
    
    def parse_scene_recursive(self, file, object, level):
        """シーン情報用再帰関数"""
        
        # 深さ分インデントする(タブを挿入)
        indent = ''
        for i in range(level):
            indent += "\t"

        self.write_and_print(file,indent + object.type)
        # 情報を取得
        trans, rot, scale = object.matrix_local.decompose()
        # 回転をQuaternionからEulerに変換
        rot = rot.to_euler()
        # ラジアンから度数法に変換
        rot.x = math.degrees(rot.x)
        rot.y = math.degrees(rot.y)
        rot.z = math.degrees(rot.z)
        # トランスフォーム情報を表示
        self.write_and_print(file,indent + "T %f %f %f" % (trans.x, trans.y, trans.z))
        self.write_and_print(file,indent + "R %f %f %f" % (rot.x, rot.y, rot.z))
        self.write_and_print(file,indent + "S %f %f %f" % (scale.x,scale.y,scale.z))
        # カスタムプロパティ'file_name'
        if "file_name" in object:
            self.write_and_print(file, indent + "N %s" % object["file_name"])
        self.write_and_print(file, indent + 'END')
        # 空白のためのPrint
        self.write_and_print(file, '')

        for child in object.children:
            self.parse_scene_recursive(file, child, level + 1)

    def export(self):
        """ファイルに出力"""

        print("シーン情報出力開始… %r" % self.filepath)

        # ファイルをテキスト形式で書き出し用にオープン
        # スコープを抜けると自動的にクローズされる
        with open(self.filepath, "wt") as file:
            # ファイルに文字列を書き込む
            self.write_and_print(file,"SCENE")

            for object in bpy.context.scene.objects:

                # 親オブジェクトのあるものはスキップ(代わりに親から呼び出すから)
                if(object.parent):
                    continue

                # シーン直下のオブジェクトのルートノード(深さ0)とし、再帰関数で走査
                self.parse_scene_recursive(file, object, 0)
               


    def execute(self, context):

        print("シーン情報をExportします")
        
        # ファイルに出力
        self.export()

        self.report({'INFO'}, "シーン情報をExportしました")
        print("シーン情報Exportしました")

        return {'FINISHED'}

# トップバーの拡張メニュー
class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "拡張メニュー by " + bl_info["author"]

    def draw(self, context):
        self.layout.operator(MYADDON_OT_stretch_vertex.bl_idname,
                             text=MYADDON_OT_stretch_vertex.bl_label)
        
        self.layout.operator(MYADDON_OT_create_ico_sphere.bl_idname,
                             text=MYADDON_OT_create_ico_sphere.bl_label)
        
        self.layout.operator(MYADDON_OT_export_scene.bl_idname,
                              text=MYADDON_OT_export_scene.bl_label)

        self.layout.operator("wm.url_open_preset",
                             text="Manual", icon='HELP')

        
    def submenu(self, context):
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# オペレータ　カスタムプロパティ['file_name']追加
class MYADDON_OT_add_filename(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_add_filename"
    bl_label = "FileName 追加"
    bl_description = "['file_name']カスタムプロパティを追加します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        # ['file_name']カスタムプロパティを追加
        context.object["file_name"] = ""

        return {"FINISHED"}

# パネル クラス
class OBJECT_PT_filename(bpy.types.Panel):
    """オブジェクトのファイルネームパネル"""
    bl_idname = "OBJECT_PT_file_name"
    bl_label = "FileName"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):

        # パネルに項目を追加
        if "file_name" in context.object:
            # 既にプロパティがあれば、プロパティを表示
            self.layout.prop(context.object, '[file_name]', text=self.bl_label)
        else:
            # プロパティが無ければ、プロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_add_filename.bl_idname)

classes = (
    MYADDON_OT_export_scene,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_stretch_vertex,
    TOPBAR_MT_my_menu,
    MYADDON_OT_add_filename,
    OBJECT_PT_filename,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    print("LevelEditor is True")
    
def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)

    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    print("LevelEditor is False")

if __name__ == "__main__":
    register()