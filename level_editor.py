import bpy

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

def register():
    print("LevelEditor is True")
    
def unregister():
    print("LevelEditor is False")
    
if __name__ == "__main__":
    register()