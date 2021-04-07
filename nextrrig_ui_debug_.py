from bpy.utils import (register_class, unregister_class)
from bpy.types import (Panel, Operator, PropertyGroup, Menu)
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty, FloatVectorProperty
import bpy

def get_rig(name):
    if name in bpy.data.objects:
        if bpy.data.objects[name].type == 'ARMATURE':
            return bpy.data.objects[name]
    return False
def ui_setup_enum(update_function, name="Name", description="Empty description", items=[], default=0):
    "method for easier creation of enums (selects)"
    return EnumProperty(
        name=name,
        description=description,
        items=items,
        update=update_function,
        default='OP'+str(default)
    )
def ui_setup_toggle(update_function, name='Name', description='Empty description', default=False):
    "method for easier creation of toggles (buttons)"
    return BoolProperty(
        name=name,
        description=description,
        update=update_function,
        default=default
    )
def ui_setup_int(update_function, name='Name', description='Empty description', default=0, min=0, max=1):
    "method for easier creation of toggles (buttons)"
    return IntProperty(
        name=name,
        description=description,
        update=update_function,
        default=default,
        min = min,
        max= max
    )
def ui_setup_string(update_function, name='Name', description='Empty description', default=""):
    "method for easier creation of toggles (buttons)"
    return StringProperty(
        name=name,
        description=description,
        update=update_function,
        default=default
    )

def get_edited_object(context):
    "return object which is currently being edited"
    if 'active_object' in context.scene:
        if context.scene['active_object']:
            return context.scene['active_object']
    return context.active_object

class VIEW3D_PT_nextr_rig_debug(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nextrrig UI Debuger"
    bl_label = "Nextrrig UI Debuger Main"

    def draw(self, context):
        layout = self.layout
        if context.active_object:
            o = get_edited_object(context)
            pinned = False
            if 'active_object' in context.scene:
                if context.scene['active_object']:
                    pinned = True 
            layout.operator('nextr_debug.pin_active_object', text="Unpin "+o.name if pinned else "Pin "+o.name, depress=pinned, icon="PINNED" if pinned else "UNPINNED")
            if o.type != 'ARMATURE':
                layout.operator('nextr.empty', text="Warning, object is not an Armature", depress=True, emboss=False)
            if "nextrrig_properties" not in o.data or 'nextrrig_attributes' not in o.data:
                layout.operator('nextr_debug.enable_rig').object_name = o.name
            else:
                layout.operator('nextr.empty', text="Object is Nextr Rig enabled", depress=True, emboss=False)
                has_outfits = o.name+" Outfits" in bpy.data.collections
                has_hair = o.name+" Hair" in bpy.data.collections
                has_body = o.name+" Body" in bpy.data.collections
                box = self.layout.box()
                box.label(text="Main Collections")
                if has_outfits:
                    box.operator('nextr.empty', text='Collection called '+o.name+" Outfits exists",depress=True, emboss=False,icon="CHECKMARK")
                else:
                    op = box.operator('nextr_debug.add_collection', text='Add collection for outfits')
                    op.collection_name = o.name+ " Outfits"
                    op.collection_parent_name = o.name
                if has_hair:
                    box.operator('nextr.empty', text='Collection called '+o.name+" Hair exists",depress=True, emboss=False,icon="CHECKMARK")
                else:
                    op = box.operator('nextr_debug.add_collection', text='Add collection for hair')
                    op.collection_name = o.name+ " Hair"
                    op.collection_parent_name = o.name
                if has_body:
                    box.operator('nextr.empty', text='Collection called '+o.name+" Body exists",depress=True, emboss=False,icon="CHECKMARK")
                else:
                    op = box.operator('nextr_debug.add_collection', text='Add collection for body')
                    op.collection_name = o.name+ " Body"
                    op.collection_parent_name = o.name

class VIEW3D_PT_nextr_rig_debug_rig_layers(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nextrrig UI Debuger"
    bl_label = "Nextrrig UI Debuger Rig Layers"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Rig Layers")
        for i in range(31):
            icon = "HIDE_OFF"
            if 'nextr_rig_layers_visibility_'+str(i) in context.scene:
                icon = "HIDE_OFF" if context.scene['nextr_rig_layers_visibility_'+str(i)] else "HIDE_ON"
            row = box.row(align=True)
            name = "Layer "+str(i+1)
            if 'nextr_rig_layers_name_'+str(i) in context.scene:
                name = context.scene['nextr_rig_layers_name_'+str(i)]
            row_box = row.box()
            row_box.label(text=name)
            row_box_row_name = row_box.row(align=True)
            row_box_row_name.prop(context.scene, 'nextr_rig_layers_visibility_'+str(i), icon=icon)
            row_box_row_name.prop(context.scene, 'nextr_rig_layers_name_'+str(i))
            row_box.label(text="Index of the rig layer")
            row_box_row_layers = row_box.row(align=True)
            row_box_row_layers.prop(context.scene, 'nextr_rig_layers_index_'+str(i))
            row_box.label(text="Row in the UI")
            row_box_row_row = row_box.row(align=True)
            row_box_row_row.prop(context.scene, 'nextr_rig_layers_row_'+str(i))

        box.operator('nextr_debug.generate_rig_layers')
class VIEW3D_PT_nextr_rig_debug_attributes(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nextrrig UI Debuger"
    bl_label = "Nextrrig UI Debuger Attributes"

    def draw(self, context):
        layout = self.layout
        if context.active_object:
            o = get_edited_object(context)
            if 'nextrrig_attributes' in o.data:
                box_outfits = layout.box()

                box_outfits.label(text="Attributes for Outfits Panel")
                render_attributes(box_outfits, 'outfits', o.data['nextrrig_attributes'])
                box_body = layout.box()
                box_body.label(text="Attributes for Body Panel")
                render_attributes(box_body, 'body', o.data['nextrrig_attributes'])
                box_rig_layers = layout.box()
                box_rig_layers.label(text="Attributes for Rig Layers Panel")
                render_attributes(box_rig_layers, 'rig', o.data['nextrrig_attributes'])
            else:
                layout.operator('nextr.empty', text="Object needs to be Nextr Rig enabled to add custom attributes to it!", depress=True, emboss=False)
class OPS_OT_EnableNextrRig(Operator):
    bl_idname = 'nextr_debug.enable_rig'
    bl_label = 'Enable Nextrrig on object'
    bl_description = 'Adds necessary props to the object'

    object_name : StringProperty()
    def execute(self, context):
        if self.object_name in bpy.data.objects:
            o = get_edited_object(context)
            master_collection = None
            if self.object_name not in bpy.data.collections:
                master_collection = bpy.data.collections.new(name=self.object_name)
                context.scene.collection.children.link(master_collection)
            else:
                master_collection = bpy.data.collections[self.object_name]
            for c in o.users_collection:
                c.objects.unlink(o)
            master_collection.objects.link(o)
            o.data['nextrrig_properties'] = {}
            o.data['nextrrig_attributes'] = {}
            bpy.context.active_object = o
        return {'FINISHED'}

class OPS_OT_AddCollection(Operator):
    bl_idname = 'nextr_debug.add_collection'
    bl_label = 'Adds collection'
    bl_description = 'Adds collection to another colection'

    collection_name: StringProperty()
    collection_parent_name: StringProperty()

    def execute(self, context):
        if self.collection_parent_name in bpy.data.collections:
            bpy.data.collections[self.collection_parent_name].children.link(bpy.data.collections.new(name=self.collection_name))
        else:
            bpy.ops.nextr_debug.add_collection(collection_name=self.collection_parent_name, collection_parent_name=bpy.data.collections[0].name)
        return {'FINISHED'}

class OPS_OT_Empty(Operator):
    "for empty operator used only as text"
    bl_idname = 'nextr.empty'
    bl_label = 'Text'
    bl_description = 'Header'
    def execute(self, context):
        return {'FINISHED'}

class OPS_OT_AddAttribute(Operator):
    bl_idname = 'nextr_debug.add_attribute'
    bl_label = 'Text'
    bl_description = 'Adds the attribute to the UI or synces it to another attribute'

    
    panel_name : StringProperty()
    parent_path :  StringProperty()

    def execute(self, context):
        try:
            bpy.ops.ui.copy_data_path_button(full_path=True)
        except:
            self.report({'WARNING'}, "Couldn't get path, invalid selection!")
            return {'FINISHED'}
        path = context.window_manager.clipboard

        name=path[:path.rindex('.')]+".name"
        try:
            name=eval(name)
        except:
            name = False

        if context.active_object:
            o = get_edited_object(context)
            if 'nextrrig_attributes' in o.data:
                arr = []
                if self.panel_name in o.data['nextrrig_attributes']:
                    arr = o.data['nextrrig_attributes'][self.panel_name]
                    try:
                        arr.append({'path': path, 'name':name})
                    except:
                        arr = []
                        arr.append({'path': path, 'name':name})
                    o.data['nextrrig_attributes'][self.panel_name] = arr
                else:
                    arr = []
                    arr.append({'path': path, 'name':name})
                    o.data['nextrrig_attributes'][self.panel_name] = arr
                print(arr)
                if name:
                    self.report({'INFO'}, 'Added attribute '+ name +' to '+o.name)
                else:
                    self.report({'INFO'}, 'Added attribute to '+o.name)
            else:
                self.report({'WARNING'}, o.name + ' is not Nextr Rig enabled! You must enable it first.')

        return {'FINISHED'}

class OPS_OT_PinActiveObject(Operator):
    bl_idname = 'nextr_debug.pin_active_object'
    bl_label = 'Pin active object'
    bl_label = 'Pins active object'
    
    def execute(self, context):
        if context.active_object:
            if 'active_object' in context.scene:
                if context.scene['active_object']:
                    context.scene['active_object'] = None
                    self.report({'INFO'}, "Unpinned "+context.active_object.name)
                else:
                    context.scene['active_object'] = context.active_object
                    self.report({'INFO'}, "Pinned "+context.active_object.name)
            else:
                context.scene['active_object'] = context.active_object
                self.report({'INFO'}, "Pinned "+context.active_object.name)
        return {'FINISHED'}

class OPS_OT_GenerateRigLayers(Operator):
    bl_idname = 'nextr_debug.generate_rig_layers'
    bl_label = 'Generate rig layers'
    bl_description = 'Generates rig layers for the selected object'

    def execute(self, context):
        if context.active_object:
            o = get_edited_object(context)
            o.data['nextrrig_rig_layers'] = {}
            nextrrig_rig_layers = []
            for i in range(31):
                nextrrig_rig_layers.append([])

            for i in range(31):
                if 'nextr_rig_layers_visibility_'+str(i) in context.scene:
                    if context.scene['nextr_rig_layers_visibility_'+str(i)]:
                        row = i
                        if 'nextr_rig_layers_row_'+str(i) in context.scene:
                            row = context.scene['nextr_rig_layers_row_'+str(i)] - 1
                        
                        name = "Layer "+str(i+1)
                        if 'nextr_rig_layers_name_'+str(i) in context.scene:
                            name = context.scene['nextr_rig_layers_name_'+str(i)]
                        
                        layer_index = i
                        if 'nextr_rig_layers_index_'+str(i) in context.scene:
                            layer_index = context.scene['nextr_rig_layers_index_'+str(i)]
                        
                        nextrrig_rig_layers[row].append({'name':name, 'index':int(layer_index)})
            o.data['nextrrig_rig_layers']['nextrrig_rig_layers'] = nextrrig_rig_layers
            self.report({'INFO'}, "Added rig layers to "+o.name)
        else:
            self.report({'ERROR'}, "No active object!")
        return {'FINISHED'}

class OPS_OT_RemoveAttribute(Operator):
    bl_idname = 'nextr_debug.remove_attribute'
    bl_label = 'Remove attribute from the UI'
    bl_description = "Removes attribute from the UI and other synced attributes too"
    path : StringProperty()
    panel_name : StringProperty()

    def execute(self, context):
        
        if context.active_object:
            o = get_edited_object(context)
            if 'nextrrig_attributes' in o.data:
                if self.panel_name in o.data['nextrrig_attributes']:
                    att = o.data['nextrrig_attributes'][self.panel_name]
                    new_att = []
                    for a in att:
                        print(a['path']," : " ,self.path)
                        if a['path'] != self.path:
                            new_att.append(a)
                    o.data['nextrrig_attributes'][self.panel_name] = new_att
                    self.report({"INFO"}, 'Removed property')
        return {'FINISHED'}

class WM_MT_button_context(Menu):
    bl_label = "Add to UI"

    def draw(self, context):
        pass

class WM_MT_add_new_attribute(Menu):
    bl_label = "Add New Attribute"
    bl_idname = 'WM_MT_add_new_attribute_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator(OPS_OT_AddAttribute.bl_idname, text="Outfits Panel").panel_name = 'outfits'
        layout.operator(OPS_OT_AddAttribute.bl_idname, text="Body Panel").panel_name = 'body'
        layout.operator(OPS_OT_AddAttribute.bl_idname, text="Rig Layers Panel").panel_name = 'rig'

class WM_MT_sync_attribute_panel(Menu):
    bl_label = "Sync To Attribute"
    bl_idname = 'WM_MT_sync_attribute_panel'

    def draw(self, context):
        layout = self.layout
        layout.menu(WM_MT_sync_attribute_outfits_menu.bl_idname, text="Outfits Panel")
        layout.menu(WM_MT_sync_attribute_body_menu.bl_idname, text="Body Panel")
        layout.menu(WM_MT_sync_attribute_rig_menu.bl_idname, text="Rig Layers Panel")

class WM_MT_sync_attribute_outfits_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = 'WM_MT_sync_attribute'
    
    def draw(self, context):
        self.layout.label(text='Attributes')
        render_attributes_in_menu(self.layout, context, 'outfits')

class WM_MT_sync_attribute_body_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = 'WM_MT_sync_attribute'
    
    def draw(self, context):
        self.layout.label(text='Attributes')
        render_attributes_in_menu(self.layout, context, 'body')

class WM_MT_sync_attribute_rig_menu(Menu):
    bl_label = "no attribute name entered!"
    bl_idname = 'WM_MT_sync_attribute'
    
    def draw(self, context):
        self.layout.label(text='Attributes')
        render_attributes_in_menu(self.layout, context, 'rig')

def render_attributes(element, panel_name, attributes):
    "renders attributes to the UI based on the panels name"
    if panel_name in attributes:
        for p in attributes[panel_name]:
            row = element.row(align=True)
            path = p['path'][:p['path'].rindex('.')]
            prop = p['path'][p['path'].rindex('.')+1:]
            if p['name']:
                row.prop(eval(path), prop, text=p['name'])
            else:
                row.prop(eval(path), prop)
            op = row.operator(OPS_OT_RemoveAttribute.bl_idname, icon="TRASH", text="")
            op.path = p['path']
            op.panel_name = panel_name

def render_attributes_in_menu(layout, context, panel):
    if context.active_object:
        o = get_edited_object(context)
        if panel in o.data['nextrrig_attributes']:
            for p in o.data['nextrrig_attributes'][panel]:
                op = layout.operator(OPS_OT_AddAttribute.bl_idname, text=p['name'])
                op.parent_path = p['path']
                op.panel_name = panel
    return layout

def render_copy_data_path(self, context):
    if 'nextrrig_attributes' in get_edited_object(context).data:
        layout = self.layout
        layout.separator()
        layout.label(text='Nextr Rig Debugger')
        layout.menu(WM_MT_add_new_attribute.bl_idname)
        layout.menu(WM_MT_sync_attribute_panel.bl_idname)



classes = (VIEW3D_PT_nextr_rig_debug,
OPS_OT_PinActiveObject,
OPS_OT_Empty,
OPS_OT_EnableNextrRig,
OPS_OT_AddCollection,
VIEW3D_PT_nextr_rig_debug_rig_layers,
OPS_OT_GenerateRigLayers,
OPS_OT_AddAttribute,
WM_MT_button_context,
VIEW3D_PT_nextr_rig_debug_attributes,
WM_MT_add_new_attribute,
WM_MT_sync_attribute_panel,
WM_MT_sync_attribute_outfits_menu,
WM_MT_sync_attribute_body_menu,
WM_MT_sync_attribute_rig_menu,
OPS_OT_RemoveAttribute)

def setup_rig_layers():
    for i in range(31):
        setattr(bpy.types.Scene, 'nextr_rig_layers_visibility_'+str(i), ui_setup_toggle(None, "","If layers is visible in the UI",False))
        setattr(bpy.types.Scene, 'nextr_rig_layers_name_'+str(i), ui_setup_string(None, "","Name of the layer in the UI","Layer "+str(i+1)))
        setattr(bpy.types.Scene, 'nextr_rig_layers_row_'+str(i), ui_setup_int(None, "","On which row is the layer going to be in the UI",i,1,32))
        setattr(bpy.types.Scene, 'nextr_rig_layers_index_'+str(i), ui_setup_int(None, "","Which rig layers is going to be affected by this toggle",i,0,31))

def register():
    setup_rig_layers()
    for c in classes:
        register_class(c)
    bpy.types.WM_MT_button_context.append(render_copy_data_path)

def unregister():
    bpy.types.WM_MT_button_context.remove(render_copy_data_path)
    for c in classes:
        unregister_class(c)
    


if __name__ == "__main__":
    register()