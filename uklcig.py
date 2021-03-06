#!/usr/bin/env python
# May 1, 2017
# License: MIT License
#####################################################################################################################################################
#Copyright (c) 2017 Pratik M Tambe (enthusiasticgeek)  <enthusiasticgeek@gmail.com> 
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#######################################################################################################################################################


# Reference Documentation
# https://www.compuphase.com/electronics/LibraryFileFormats.pdf

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from time import gmtime, strftime
import cairo
import math
import signal
import os

UI_INFO = """
<ui>
  <popup name='PopupMenu'>
    <menuitem action='AddPin' />
    <menuitem action='RemovePin' />
  </popup>
</ui>
"""

class MouseButtons:

    LEFT_BUTTON = 1
    CENTER_BUTTON = 2
    RIGHT_BUTTON = 3

class Directions:
 
    WEST = 1
    EAST = 2
    NORTH = 3
    SOUTH = 4

class UKLCIG(Gtk.Window):

    def __init__(self):
        super(UKLCIG, self).__init__()

        self.init_ui()

    def init_ui(self):

        self.pins_west = []
        self.pins_east = []
        self.pins_north = []
        self.pins_south = []

        self.cur_direction = 0
        self.populate = []
        self.RESULT = ''
        self.pin_length = 300
        self.pins_distance = 5
        self.pin_width = 5
        self.size_signal_name = 10
        self.size_pin_name = 10
 
        #X, Name, Pin, X, Y,   Length, Orientation, sizenum sizename part dmg_type     Type shape 
        #X  PB11  A1 -750 8300  300       R           10    10        1      1          I   V
        self.cur_pin_selected = -1
        self.Orientation = 'L'
        self.Type = None
        self.Shape = None
        self.invisible = ''

        self.cur_pin_west = 0       
        self.cur_pin_east = 0       
        self.cur_pin_north = 0       
        self.cur_pin_south = 0       
 
        self.action_group = Gtk.ActionGroup("my_actions")
        self.add_edit_menu_actions(self.action_group)
        #self.action_group.remove_action(
        #    action_group.get_action("RemovePin"))

        # Fist make sure to begin with we don't show add pin or remove pin on right click
        self.action_group.get_action("AddPin").set_sensitive(False)
        self.action_group.get_action("RemovePin").set_sensitive(False)
 
        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(self.action_group)
        self.popup = uimanager.get_widget("/PopupMenu")

        # signal handler setup
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGUSR1, self.signal_handler)

        self.BEGIN_MOUSE_X = 0
        self.BEGIN_MOUSE_Y = 0
        self.END_MOUSE_X = 0
        self.END_MOUSE_Y = 0
        self.MOUSE_X = 0
        self.MOUSE_Y = 0
        self.PIN_X = 0
        self.PIN_Y = 0

        self.ic_width = 200
        self.ic_length = 400
        self.sides = 4

        # Can we populate the total pins along the perimeter?
        perimeter = 2 * (self.ic_width + self.ic_length)

        # assume pin width = 5 and gap between pins = 5
        self.max_pins_per_width = self.ic_width / (self.pin_width+self.pins_distance)
        self.max_pins_per_length = self.ic_length / (self.pin_width+self.pins_distance)

        # Max pins that can be drawn sanely
        max_pins = 0
        if (self.sides == 2):
            max_pins = 2 * (self.max_pins_per_length)
        elif (self.sides == 4):
            max_pins = 2 * (self.max_pins_per_width + self.max_pins_per_length)

        # Max pins requested is less than or equal to pins that may be drawn?
        self.total_pins = max_pins

        self.shape_invisible_pin_flag = False
        self.crosshair = False

        self.darea = Gtk.DrawingArea()
        self.darea.set_size_request(self.ic_width+200, self.ic_length+200)
        self.darea.connect("draw", self.on_draw)
        self.vbox = Gtk.VBox(False,2)
        self.vbox.pack_start(self.darea, False, False, 0)

        self.darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK |
                              Gdk.EventMask.BUTTON1_MOTION_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        self.darea.connect("button-press-event", self.on_button_press)
        self.darea.connect("button-release-event", self.on_button_release)
        self.darea.connect("motion_notify_event", self.on_motion_notify_event)

        self.set_title("UNOFFICIAL KiCAD LIBRARY COMPONENT IC GENERATOR [UKLCIG]")
        self.resize(1000, 1000)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)

        self.hbox = Gtk.HBox(False,2)
        self.vbox0 = Gtk.VBox(False,2)
        self.vbox1 = Gtk.VBox(False,2)
        self.vbox2 = Gtk.VBox(False,2)
        self.vbox3 = Gtk.VBox(False,2)
        self.vbox4 = Gtk.VBox(False,2)
        self.vbox5 = Gtk.VBox(False,2)
        self.vbox6 = Gtk.VBox(False,2)
        self.vbox7 = Gtk.VBox(False,2)
        self.hbox.pack_start(self.vbox0, False, False, 0)
        self.hbox.pack_start(self.vbox1, False, False, 0)
        self.hbox.pack_start(self.vbox2, False, False, 0)
        self.hbox.pack_start(self.vbox3, False, False, 0)
        self.hbox.pack_start(self.vbox4, False, False, 0)
        self.hbox.pack_start(self.vbox5, False, False, 0)
        self.hbox.pack_start(self.vbox6, False, False, 0)
        self.hbox.pack_start(self.vbox7, False, False, 0)
        self.vbox.pack_start(self.hbox, False, False, 0)

        hseparator = Gtk.HSeparator()
        hseparator1 = Gtk.HSeparator()
        self.ic_name_label = Gtk.Label("")
        self.ic_name_label.set_label("<b>IC Name</b>")
        self.ic_name_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.ic_name_label.set_use_markup(True)
        self.ic_name_entry = Gtk.Entry()
        self.ic_name_entry.set_visibility(True)
        self.ic_name_entry.set_max_length(32)
        self.ic_dimensions_label = Gtk.Label("")
        self.ic_dimensions_label.set_label("<b>IC Dimensions (WxL)</b>")
        self.ic_dimensions_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.ic_dimensions_label.set_use_markup(True)
        self.ic_width_entry = Gtk.Entry()
        self.ic_width_entry.set_visibility(True)
        self.ic_width_entry.set_max_length(5)
        self.ic_width_entry.set_text(str(self.ic_width))
        self.ic_length_entry = Gtk.Entry()
        self.ic_length_entry.set_visibility(True)
        self.ic_length_entry.set_max_length(5)
        self.ic_length_entry.set_text(str(self.ic_length))

        self.vbox0.pack_start(hseparator, False, False, 0)
        self.vbox0.pack_start(self.ic_name_label, False, False, 0)
        self.vbox0.pack_start(self.ic_name_entry, False, False, 0)
        self.vbox0.pack_start(hseparator1, False, False, 0)
        self.vbox0.pack_start(self.ic_dimensions_label, False, False, 0)
        self.vbox0.pack_start(self.ic_width_entry, False, False, 0)
        self.vbox0.pack_start(self.ic_length_entry, False, False, 0)

        hseparator = Gtk.HSeparator()
        hseparator1 = Gtk.HSeparator()
        self.pins_distance_label = Gtk.Label("")
        self.pins_distance_label.set_label("<b>Distance Between Pins</b>")
        self.pins_distance_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.pins_distance_label.set_use_markup(True)
        self.pins_distance_entry = Gtk.Entry()
        self.pins_distance_entry.set_visibility(True)
        self.pins_distance_entry.set_max_length(5)
        self.pins_distance_entry.set_text("5")
        self.pin_width_label = Gtk.Label("")
        self.pin_width_label.set_label("<b>Pin Width</b>")
        self.pin_width_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.pin_width_label.set_use_markup(True)
        self.pin_width_entry = Gtk.Entry()
        self.pin_width_entry.set_visibility(True)
        self.pin_width_entry.set_max_length(5)
        self.pin_width_entry.set_text("5")
        self.ic_dimensions_button = Gtk.Button("")
        for child in self.ic_dimensions_button :
            child.set_label("<b>Update IC Dimensions</b>")
            child.set_use_markup(True)
            child.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkred")[1])
        self.ic_dimensions_button.connect("clicked", self.on_ic_dimensions_button, "ic dimensions update button")

        self.vbox1.pack_start(hseparator, False, False, 0)
        self.vbox1.pack_start(self.pins_distance_label, False, False, 0)
        self.vbox1.pack_start(self.pins_distance_entry, False, False, 0)
        self.vbox1.pack_start(self.pin_width_label, False, False, 0)
        self.vbox1.pack_start(self.pin_width_entry, False, False, 0)
        self.vbox1.pack_start(hseparator1, False, False, 0)
        self.vbox1.pack_start(self.ic_dimensions_button, False, False, 0)

        hseparator = Gtk.HSeparator()
        hseparator1 = Gtk.HSeparator()
        self.signal_name_label = Gtk.Label("")
        self.signal_name_label.set_label("<b>Signal Name</b>")
        self.signal_name_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.signal_name_label.set_use_markup(True)
        self.signal_name_entry = Gtk.Entry()
        self.signal_name_entry.set_visibility(True)
        self.signal_name_entry.set_max_length(32)
        self.signal_name_entry.set_text("Enter Signal Name (e.g. GND)")
        self.cur_signal_name_label = Gtk.Label("")
        self.cur_signal_name_label.set_label("<b>N/A</b>")
        self.cur_signal_name_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("purple")[1])
        self.cur_signal_name_label.set_use_markup(True)
        self.size_signal_name_label = Gtk.Label("")
        self.size_signal_name_label.set_label("<b>Signal Text Size</b>")
        self.size_signal_name_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.size_signal_name_label.set_use_markup(True)
        self.size_signal_name_entry = Gtk.Entry()
        self.size_signal_name_entry.set_visibility(True)
        self.size_signal_name_entry.set_max_length(5)
        self.size_signal_name_entry.set_text("10")

        self.vbox2.pack_start(hseparator, False, False, 0)
        self.vbox2.pack_start(self.signal_name_label, False, False, 0)
        self.vbox2.pack_start(self.signal_name_entry, False, False, 0)
        self.vbox2.pack_start(self.cur_signal_name_label, False, False, 0)
        self.vbox2.pack_start(hseparator1, False, False, 0)
        self.vbox2.pack_start(self.size_signal_name_label, False, False, 0)
        self.vbox2.pack_start(self.size_signal_name_entry, False, False, 0)

        hseparator = Gtk.HSeparator()
        hseparator1 = Gtk.HSeparator()
        self.pin_name_label = Gtk.Label("")
        self.pin_name_label.set_label("<b>Pin Name</b>")
        self.pin_name_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.pin_name_label.set_use_markup(True)
        self.pin_name_entry = Gtk.Entry()
        self.pin_name_entry.set_visibility(True)
        self.pin_name_entry.set_max_length(32)
        self.pin_name_entry.set_text("Enter Pin Name (e.g. A1)")
        self.pins_distance_label = Gtk.Label("")
        self.cur_pin_name_label = Gtk.Label("")
        self.cur_pin_name_label.set_label("<b>N/A</b>")
        self.cur_pin_name_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("purple")[1])
        self.cur_pin_name_label.set_use_markup(True)
        self.size_pin_name_label = Gtk.Label("")
        self.size_pin_name_label.set_label("<b>Pin Text Size</b>")
        self.size_pin_name_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.size_pin_name_label.set_use_markup(True)
        self.size_pin_name_entry = Gtk.Entry()
        self.size_pin_name_entry.set_visibility(True)
        self.size_pin_name_entry.set_max_length(5)
        self.size_pin_name_entry.set_text("10")

        self.vbox3.pack_start(hseparator, False, False, 0)
        self.vbox3.pack_start(self.pin_name_label, False, False, 0)
        self.vbox3.pack_start(self.pin_name_entry, False, False, 0)
        self.vbox3.pack_start(self.cur_pin_name_label, False, False, 0)
        self.vbox3.pack_start(hseparator1, False, False, 0)
        self.vbox3.pack_start(self.size_pin_name_label, False, False, 0)
        self.vbox3.pack_start(self.size_pin_name_entry, False, False, 0)

        #hseparator = Gtk.HSeparator()
        #self.orientation_label = Gtk.Label("")
        #self.orientation_label.set_label("<b>Orientation</b>")
        #self.orientation_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        #self.orientation_label.set_use_markup(True)
        #self.orientation_combobox = Gtk.ComboBox()
        #self.orientation_liststore = Gtk.ListStore(str)
        #self.orientation_cell = Gtk.CellRendererText()
        #self.orientation_combobox.pack_start(self.orientation_cell,0)
        #self.orientation_combobox.add_attribute(self.orientation_cell, 'text', 0)
        #self.orientation_combobox.set_wrap_width(2)
        #self.orientation_liststore.append(['Left'])
        #self.orientation_liststore.append(['Right'])
        #self.orientation_liststore.append(['Up'])
        #self.orientation_liststore.append(['Down'])
        #self.orientation_combobox.set_model(self.orientation_liststore)
        #self.orientation_combobox.connect('changed', self.orientation_callback)
        #self.orientation_combobox.set_active(0)
        #self.cur_orientation_label = Gtk.Label("")
        #self.cur_orientation_label.set_label("<b>N/A</b>")
        #self.cur_orientation_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("purple")[1])
        #self.cur_orientation_label.set_use_markup(True)

        #self.vbox3.pack_start(hseparator, False, False, 0)
        #self.vbox3.pack_start(self.orientation_label, False, False, 0)
        #self.vbox3.pack_start(self.orientation_combobox, False, False, 0)
        #self.vbox3.pack_start(self.cur_orientation_label, False, False, 0)

        hseparator = Gtk.HSeparator()
        hseparator1 = Gtk.HSeparator()
        self.type_label = Gtk.Label("")
        self.type_label.set_label("<b>Type</b>")
        self.type_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.type_label.set_use_markup(True)
        self.type_combobox = Gtk.ComboBox()
        self.type_liststore = Gtk.ListStore(str)
        self.type_cell = Gtk.CellRendererText()
        self.type_combobox.pack_start(self.type_cell,0)
        self.type_combobox.add_attribute(self.type_cell, 'text', 0)
        self.type_combobox.set_wrap_width(5)
        self.type_liststore.append(['Input (I)'])
        self.type_liststore.append(['Output (O)'])
        self.type_liststore.append(['Bidirectional (B)'])
        self.type_liststore.append(['Tristate (T)'])
        self.type_liststore.append(['Passive (P)'])
        self.type_liststore.append(['Open Collector (C)'])
        self.type_liststore.append(['Open Emitter (E)'])
        self.type_liststore.append(['Not Connected (N)'])
        self.type_liststore.append(['Unspecified (U)'])
        self.type_liststore.append(['Power Input (W)'])
        self.type_liststore.append(['Power Output (w)'])
        self.type_combobox.set_model(self.type_liststore)
        self.type_combobox.connect('changed', self.type_callback)
        self.type_combobox.set_active(0)
        self.cur_type_label = Gtk.Label("")
        self.cur_type_label.set_label("<b>N/A</b>")
        self.cur_type_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("purple")[1])
        self.cur_type_label.set_use_markup(True)
        self.pin_length_label = Gtk.Label("")
        self.pin_length_label.set_label("<b>Pin Length</b>")
        self.pin_length_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.pin_length_label.set_use_markup(True)
        self.pin_length_entry = Gtk.Entry()
        self.pin_length_entry.set_visibility(True)
        self.pin_length_entry.set_max_length(5)
        self.pin_length_entry.set_text("300")

        self.vbox4.pack_start(hseparator, False, False, 0)
        self.vbox4.pack_start(self.type_label, False, False, 0)
        self.vbox4.pack_start(self.type_combobox, False, False, 0)
        self.vbox4.pack_start(self.cur_type_label, False, False, 0)
        self.vbox4.pack_start(hseparator1, False, False, 0)
        self.vbox4.pack_start(self.pin_length_label, False, False, 0)
        self.vbox4.pack_start(self.pin_length_entry, False, False, 0)

        hseparator = Gtk.HSeparator()
        self.shape_label = Gtk.Label("")
        self.shape_label.set_label("<b>Shape</b>")
        self.shape_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.shape_label.set_use_markup(True)
        self.shape_combobox = Gtk.ComboBox()
        self.shape_liststore = Gtk.ListStore(str)
        self.shape_cell = Gtk.CellRendererText()
        self.shape_combobox.pack_start(self.shape_cell,0)
        self.shape_combobox.add_attribute(self.shape_cell, 'text', 0)
        self.shape_combobox.set_wrap_width(4)
        self.shape_liststore.append(['Default'])
        self.shape_liststore.append(['Inverted (I)'])
        self.shape_liststore.append(['Clock (C)'])
        self.shape_liststore.append(['Inverted Clock (IC)'])
        self.shape_liststore.append(['Input-Low (L)'])
        self.shape_liststore.append(['Output-Low (V)'])
        self.shape_liststore.append(['Clock-Input-Low (CL)'])
        self.shape_combobox.set_model(self.shape_liststore)
        self.shape_combobox.connect('changed', self.shape_callback)
        self.shape_combobox.set_active(0)
        self.cur_shape_label = Gtk.Label("")
        self.cur_shape_label.set_label("<b>N/A</b>")
        self.cur_shape_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("purple")[1])
        self.cur_shape_label.set_use_markup(True)
        self.shape_invisible_button = Gtk.CheckButton("")
        for child in self.shape_invisible_button :
            child.set_label("<b>Invisible Pin</b>")
            child.set_use_markup(True)
            child.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkred")[1])
        self.shape_invisible_button.connect("clicked", self.on_shape_invisible_button, "invisible pin button")

        self.vbox5.pack_start(hseparator, False, False, 0)
        self.vbox5.pack_start(self.shape_label, False, False, 0)
        self.vbox5.pack_start(self.shape_combobox, False, False, 0)
        self.vbox5.pack_start(self.shape_invisible_button, False, False, 0)
        self.vbox5.pack_start(self.cur_shape_label, False, False, 0)

        hseparator = Gtk.HSeparator()
        hseparator1 = Gtk.HSeparator()
        self.update_pin_label = Gtk.Label("")
        self.update_pin_label.set_label("<b>Update Pin</b>")
        self.update_pin_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("red")[1])
        self.update_pin_label.set_use_markup(True)
        self.update_inst_label = Gtk.Label("")
        self.update_inst_label.set_label("<b>1.Right click any IC boundary unit marker\n2.Click 'AddPin'\n3.Double click to select added pin\n4.Select signal/pin attributes\n5.Click the button below</b>")
        self.update_inst_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("blue")[1])
        self.update_inst_label.set_use_markup(True)
        self.update_pin_button = Gtk.Button("")
        for child in self.update_pin_button :
            child.set_label("<b>Update Pin Attributes</b>")
            child.set_use_markup(True)
            child.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkred")[1])
        self.crosshair_button = Gtk.CheckButton("")
        for child in self.crosshair_button :
            child.set_label("<b>Cross Hair</b>")
            child.set_use_markup(True)
            child.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkred")[1])
        self.crosshair_button.connect("clicked", self.on_crosshair_button, "crosshair button")

        self.vbox6.pack_start(hseparator, False, False, 0)
        self.vbox6.pack_start(self.update_pin_label, False, False, 0)
        self.vbox6.pack_start(hseparator1, False, False, 0)
        self.vbox6.pack_start(self.update_inst_label, False, False, 0)
        self.vbox6.pack_start(self.update_pin_button, False, False, 0)
        self.vbox6.pack_start(self.crosshair_button, False, False, 0)
      
        self.update_pin_button.connect("clicked", self.on_update_pin_button, "update pins")

        hseparator = Gtk.HSeparator()
        hseparator1 = Gtk.HSeparator()
        hseparator2 = Gtk.HSeparator()
        self.save_label = Gtk.Label("")
        self.save_label.set_label("<b>Save Library Component</b>")
        self.save_label.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkgreen")[1])
        self.save_label.set_use_markup(True)
        #self.save_entry = Gtk.Entry()
        #self.save_entry.set_visibility(True)
        #self.save_entry.set_max_length(32)
        #self.save_entry.set_text("SAVE IC Library")
        self.save_button = Gtk.Button("")
        for child in self.save_button :
            child.set_label("<b>SAVE</b>")
            child.set_use_markup(True)
            child.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkred")[1])
        self.save_button.connect("clicked", self.on_save_button)
        self.ic_name_entry.set_text("Enter IC Name")
        self.about_button = Gtk.Button("")
        for child in self.about_button :
            child.set_label("<b>About</b>")
            child.set_use_markup(True)
            child.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkred")[1])
        self.about_button.connect("clicked", self.on_about_button)
        self.exit_button = Gtk.Button("")
        for child in self.exit_button :
            child.set_label("<b>Exit</b>")
            child.set_use_markup(True)
            child.modify_fg(Gtk.StateType.NORMAL, Gdk.Color.parse("darkred")[1])
        self.exit_button.connect("clicked", self.on_exit_button)

        self.vbox7.pack_start(hseparator, False, False, 0)
        self.vbox7.pack_start(self.save_label, False, False, 0)
        self.vbox7.pack_start(self.save_button, False, False, 0)
        self.vbox7.pack_start(hseparator1, False, False, 0)
        self.vbox7.pack_start(self.about_button, False, False, 0)
        self.vbox7.pack_start(hseparator2, False, False, 0)
        self.vbox7.pack_start(self.exit_button, False, False, 0)

        self.add(self.vbox)
        self.show_all()
   
    def on_save_button(self, widget):

        # If there are spaces then reject
        if ' ' in self.ic_name_entry.get_text():
           dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "IC name contain spaces")
           dialog.format_secondary_text(
                    "IC name cannot contain spaces.")
           dialog.run()
           dialog.destroy()
           return False

        #self.LIBRARY = str(self.save_entry.get_text())
        dialog = Gtk.FileChooserDialog("Please choose a kicad file", self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        filter_kicad = Gtk.FileFilter()
        filter_kicad.set_name("KiCAD library component")
        filter_kicad.add_pattern("*.lib")
        dialog.add_filter(filter_kicad)
        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
           #print("File selected: " + dialog.get_filename())
           #buf = self.view.get_buffer()
           #self.RESULT = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)
           kicad_filename = dialog.get_filename()
           # check file extension. If no file extension add it
           if ".lib" not in kicad_filename:
              kicad_filename += ".lib"
           # check if file with the same filename exists -> Prompt user yes or no to overwrite
           # Case I: File exists
           if os.path.exists(kicad_filename) == True:
              dialog2 = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                  Gtk.ButtonsType.YES_NO, "The file "+kicad_filename+" exists.\nOverwrite it?")
              dialog2.format_secondary_text(
                  "Do you want to overwrite file "+kicad_filename+".")
              response2 = dialog2.run()
              # If the user responds NO. Do nothing.
              if response2 == Gtk.ResponseType.NO:
                 dialog2.destroy()
                 dialog.destroy()
                 return False
              # If the user responds YES. Overwrite the file.
              elif response2 == Gtk.ResponseType.YES:
                 try:
                     open(kicad_filename, 'w').write(self.RESULT)
                 except SomeError as err:
                     print('Could not save %s: %s' % (kicad_filename, err))
                 dialog2.destroy()
                 dialog.destroy()
                 return False
           # Case II: File doesn't already exist -> create it.
           try:
                open(kicad_filename, 'w').write(self.RESULT)
           except SomeError as err:
                print('Could not save %s: %s' % (kicad_filename, err))
        elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")
        dialog.destroy()
        return False


    def on_ic_dimensions_button(self, widget, data=None):


        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK_CANCEL, "This will reset IC parameters")
        dialog.format_secondary_text(
            "This will reset the IC parameters. Do you wish to proceed?")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:

            #Empty list and initialize variables
            self.cur_pin_west = 0
            self.cur_pin_east = 0
            self.cur_pin_north = 0
            self.cur_pin_south = 0

            self.pins_west[:] = []
            self.pins_east[:] = []
            self.pins_north[:] = []
            self.pins_south[:] = []

            self.cur_direction = 0
            self.populate[:] = []

            self.BEGIN_MOUSE_X = 0
            self.BEGIN_MOUSE_Y = 0
            self.END_MOUSE_X = 0
            self.END_MOUSE_Y = 0
            self.MOUSE_X = 0
            self.MOUSE_Y = 0
            self.PIN_X = 0
            self.PIN_Y = 0

        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            return False

        dialog.destroy()

        # Verify if text boxes are numbers
        if self.ic_width_entry.get_text().isdigit()==False or self.ic_length_entry.get_text().isdigit()==False or self.pins_distance_entry.get_text().isdigit()==False or self.pin_width_entry.get_text().isdigit()==False:
           dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "One or more Signal or Pin attributes not a valid number")
           dialog.format_secondary_text(
                    "Signal or Pin attibutes (other than names) should all be numeric.")
           dialog.run()
           dialog.destroy()
           return False


        self.ic_width = int(self.ic_width_entry.get_text())
        self.ic_length = int(self.ic_length_entry.get_text())
        self.pins_distance = int(self.pins_distance_entry.get_text())
        self.pin_width = int(self.pin_width_entry.get_text())

        # Can we populate the total pins along the perimeter?
        perimeter = 2 * (self.ic_width + self.ic_length)

        # assume pin width = 5 and gap between pins = 5
        self.max_pins_per_width = self.ic_width / (self.pin_width+self.pins_distance)
        self.max_pins_per_length = self.ic_length / (self.pin_width+self.pins_distance)

        # Max pins that can be drawn sanely
        max_pins = 0
        if (self.sides == 2):
            max_pins = 2 * (self.max_pins_per_length)
        elif (self.sides == 4):
            max_pins = 2 * (self.max_pins_per_width + self.max_pins_per_length)

        # Max pins requested is less than or equal to pins that may be drawn?
        self.total_pins = max_pins


    def on_update_pin_button(self, widget, data=None):
        # Redo IC dimensions - TODO check if this portion makes sense or is redundant
 
        # If there are spaces then reject
        if ' ' in (self.signal_name_entry.get_text() or self.pin_name_entry.get_text() or self.pin_length_entry.get_text() or self.size_signal_name_entry.get_text() or self.size_pin_name_entry.get_text()):
           dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "Signal or Pin attributes contain spaces")
           dialog.format_secondary_text(
                    "Signal or Pin attibutes cannot contain spaces.")
           dialog.run()
           dialog.destroy()
           return False

        # Verify if text boxes are numbers
        if self.ic_width_entry.get_text().isdigit()==False or self.ic_length_entry.get_text().isdigit()==False or self.pin_length_entry.get_text().isdigit()==False or self.size_signal_name_entry.get_text().isdigit()==False or self.size_pin_name_entry.get_text().isdigit()==False:
           dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "One or more Signal or Pin attributes not a valid number")
           dialog.format_secondary_text(
                    "Signal or Pin attibutes (other than names) should all be numeric.")
           dialog.run()
           dialog.destroy()
           return False

        # Otherwise proceed
        self.ic_width = int(self.ic_width_entry.get_text())
        self.ic_length = int(self.ic_length_entry.get_text())
        self.pin_length = int(self.pin_length_entry.get_text())
        self.size_signal_name = int(self.size_signal_name_entry.get_text())
        self.size_pin_name = int(self.size_pin_name_entry.get_text())

        # Can we populate the total pins along the perimeter?
        perimeter = 2 * (self.ic_width + self.ic_length)

        # assume pin width = 5 and gap between pins = 5
        self.max_pins_per_width = self.ic_width / (self.pin_width+self.pins_distance)
        self.max_pins_per_length = self.ic_length / (self.pin_width+self.pins_distance)

        # Max pins that can be drawn sanely
        max_pins = 0
        if (self.sides == 2):
            max_pins = 2 * (self.max_pins_per_length)
        elif (self.sides == 4):
            max_pins = 2 * (self.max_pins_per_width + self.max_pins_per_length)

        # Max pins requested is less than or equal to pins that may be drawn?
        self.total_pins = max_pins

        if self.cur_pin_selected != -1:
           nom = [x for x in self.populate if (x[0] == self.cur_direction and x[1] == self.cur_pin_selected)]
           #Entry already exists simply update the contents
           if nom:
              for i in range( len( self.populate ) ):
               #X, Name, Pin, X, Y,   Length, Orientation, sizenum sizename part dmg_type     Type shape 
               #X  PB11  A1 -750 8300  300       R           10    10        1      1          I   V
                 if self.populate[i][0] == self.cur_direction and self.populate[i][1] == self.cur_pin_selected:
                    self.populate[i][2] = self.signal_name_entry.get_text()
                    self.populate[i][3] = self.pin_name_entry.get_text()
                    self.populate[i][4] = self.PIN_X
                    self.populate[i][5] = self.PIN_Y
                    self.populate[i][6] = self.pin_length
                    self.populate[i][7] = self.Orientation
                    self.populate[i][8] = self.size_pin_name
                    self.populate[i][9] = self.size_signal_name
                    self.populate[i][10] = 1 # We will create only one part rather than multiple parts for the same component
                    self.populate[i][11] = 1 # We will set dmg_type to always 1
                    self.populate[i][12] = self.Type
                    self.populate[i][13] = self.Shape
                    self.cur_signal_name_label.set_label("<b>"+str(self.populate[i][2])+"</b>")
                    self.cur_signal_name_label.set_use_markup(True)
                    self.cur_pin_name_label.set_label("<b>"+str(self.populate[i][3])+"</b>")
                    self.cur_pin_name_label.set_use_markup(True)
                    #self.cur_orientation_label.set_label("<b>"+str(self.populate[i][7])+"</b>")
                    #self.cur_orientation_label.set_use_markup(True)
                    self.cur_type_label.set_label("<b>"+str(self.populate[i][12])+"</b>")
                    self.cur_type_label.set_use_markup(True)
                    self.cur_shape_label.set_label("<b>"+str(self.populate[i][13])+"</b>")
                    self.cur_shape_label.set_use_markup(True)
           #Create the new entry
           else:
               #X, Name, Pin, X, Y,   Length, Orientation, sizenum sizename part dmg_type     Type shape 
               #X  PB11  A1 -750 8300  300       R           10    10        1      1          I   V
               self.populate.append([self.cur_direction,self.cur_pin_selected,self.signal_name_entry.get_text(),self.pin_name_entry.get_text(),self.PIN_X,self.PIN_Y,self.pin_length,self.Orientation,self.size_pin_name,self.size_signal_name,1,1,self.Type,self.Shape])
               for i in range( len( self.populate ) ):
               #X, Name, Pin, X, Y,   Length, Orientation, sizenum sizename part dmg_type     Type shape 
               #X  PB11  A1 -750 8300  300       R           10    10        1      1          I   V
                 if self.populate[i][0] == self.cur_direction and self.populate[i][1] == self.cur_pin_selected:
                    self.cur_signal_name_label.set_label("<b>"+str(self.populate[i][2])+"</b>")
                    self.cur_signal_name_label.set_use_markup(True)
                    self.cur_pin_name_label.set_label("<b>"+str(self.populate[i][3])+"</b>")
                    self.cur_pin_name_label.set_use_markup(True)
                    #self.cur_orientation_label.set_label("<b>"+str(self.populate[i][7])+"</b>")
                    #self.cur_orientation_label.set_use_markup(True)
                    self.cur_type_label.set_label("<b>"+str(self.populate[i][12])+"</b>")
                    self.cur_type_label.set_use_markup(True)
                    self.cur_shape_label.set_label("<b>"+str(self.populate[i][13])+"</b>")
                    self.cur_shape_label.set_use_markup(True)
               #print data

    def on_exit_button(self, widget):
        Gtk.main_quit()

    def on_about_button(self, widget):
        about = Gtk.AboutDialog(UKLCIG,self)
        about.set_program_name("Unofficial KiCAD Library Component IC Generator (UKLCIG)")
        about.set_version("Version: 0.1")
        about.set_copyright("Copyright (c) 2017 Pratik M Tambe <enthusiasticgeek@gmail.com>")
        about.set_comments("A simple tool for generating KiCAD IC Library Component")
        about.set_website("https://github.com/enthusiasticgeek")
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_size("UKLCIG.png", 300, 185))
        about.run()
        about.destroy()

    # The data passed to this method is printed to stdout
    def on_crosshair_button(self, widget, data=None):
        print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
        if widget.get_active() == True:
           self.crosshair = True
        elif widget.get_active() == False:
           self.crosshair = False

    # The data passed to this method is printed to stdout
    def on_shape_invisible_button(self, widget, data=None):
        print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
        if widget.get_active() == True:
           self.invisible = 'N'
        elif widget.get_active() == False:
           self.invisible = ''

    def orientation_callback(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            print model[index][0], 'selected'
            if index == 0:
               self.Orientation = 'L'
            if index == 1:
               self.Orientation = 'R'
            if index == 2:
               self.Orientation = 'U'
            if index == 3:
               self.Orientation = 'D'
        return

    def type_callback(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            print model[index][0], 'selected'
            if index == 0:
               self.Type = 'I'
            if index == 1:
               self.Type = 'O'
            if index == 2:
               self.Type = 'B'
            if index == 3:
               self.Type = 'T'
            if index == 4:
               self.Type = 'P'
            if index == 5:
               self.Type = 'C'
            if index == 6:
               self.Type = 'E'
            if index == 7:
               self.Type = 'N'
            if index == 8:
               self.Type = 'U'
            if index == 9:
               self.Type = 'W'
            if index == 10:
               self.Type = 'w'
        return

    def shape_callback(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index > -1:
            print model[index][0], 'selected'
            if index == 0:
               self.Shape = self.invisible+' '
            if index == 1:
               self.Shape = self.invisible+'I'
            if index == 2:
               self.Shape = self.invisible+'C'
            if index == 3:
               self.Shape = self.invisible+'IC'
            if index == 4:
               self.Shape = self.invisible+'L'
            if index == 5:
               self.Shape = self.invisible+'V'
            if index == 6:
               self.Shape = self.invisible+'CL'
        return

    def create_ui_manager(self):
        uimanager = Gtk.UIManager()
        # Throws exception if something went wrong
        uimanager.add_ui_from_string(UI_INFO)
        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager

    def on_menu_others(self, widget):
        #print("Menu item " + widget.get_name() + " was selected >")
        #w, h = self.darea.get_size()
        w = self.darea.get_allocation().width
        h = self.darea.get_allocation().height

        if (self.MOUSE_X-w/2) >= -self.ic_width/2-10 and (self.MOUSE_X-w/2) < -self.ic_width/2-10+10 and (self.MOUSE_Y-h/2) >= -self.ic_length/2+0*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_Y-h/2) < -self.ic_length/2+self.max_pins_per_length*(self.pin_width+self.pins_distance)+5+5:
          #print "West " + str(self.cur_pin_west)       
          if self.cur_pin_west not in self.pins_west:
             if widget.get_name() == 'AddPin':
                self.pins_west.append(self.cur_pin_west)
          if self.cur_pin_west in self.pins_west:
             if widget.get_name() == 'RemovePin':
                while self.cur_pin_west in self.pins_west: self.pins_west.remove(self.cur_pin_west) 
                #Also remove from the populate list
                self.populate = [x for x in self.populate if not (x[0] == Directions.WEST and x[1] == self.cur_pin_west) ]

        if (self.MOUSE_X-w/2) >= self.ic_width/2 and (self.MOUSE_X-w/2) < self.ic_width/2+10+10 and (self.MOUSE_Y-h/2) >= -self.ic_length/2+0*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_Y-h/2) < -self.ic_length/2+self.max_pins_per_length*(self.pin_width+self.pins_distance)+5+5:
          #print "East " + str(self.cur_pin_east)
          if self.cur_pin_east not in self.pins_east:
             if widget.get_name() == 'AddPin':
                self.pins_east.append(self.cur_pin_east)
          if self.cur_pin_east in self.pins_east:
             if widget.get_name() == 'RemovePin':
                while self.cur_pin_east in self.pins_east: self.pins_east.remove(self.cur_pin_east) 
                #Also remove from the populate list
                self.populate = [x for x in self.populate if not (x[0] == Directions.EAST and x[1] == self.cur_pin_east) ]

        if (self.MOUSE_X-w/2) >= -self.ic_width/2+0*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_X-w/2) < -self.ic_width/2+self.max_pins_per_width*(self.pin_width+self.pins_distance)+5+5 and (self.MOUSE_Y-h/2) >= -self.ic_length/2-10-10 and (self.MOUSE_Y-h/2) < -self.ic_length/2-10+10:
          #print "North " + str(self.cur_pin_north)
          if self.cur_pin_north not in self.pins_north:
             if widget.get_name() == 'AddPin':
                self.pins_north.append(self.cur_pin_north)
          if self.cur_pin_north in self.pins_north:
             if widget.get_name() == 'RemovePin':
                while self.cur_pin_north in self.pins_north: self.pins_north.remove(self.cur_pin_north) 
                #Also remove from the populate list
                self.populate = [x for x in self.populate if not (x[0] == Directions.NORTH and x[1] == self.cur_pin_north) ]

        if (self.MOUSE_X-w/2) >= -self.ic_width/2+0*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_X-w/2) < -self.ic_width/2+self.max_pins_per_width*(self.pin_width+self.pins_distance)+5+5 and (self.MOUSE_Y-h/2) >= self.ic_length/2-10 and (self.MOUSE_Y-h/2) < self.ic_length/2+20:
          #print "South " + str(self.cur_pin_south)
          if self.cur_pin_south not in self.pins_south:
             if widget.get_name() == 'AddPin':
                self.pins_south.append(self.cur_pin_south)
          if self.cur_pin_south in self.pins_south:
             if widget.get_name() == 'RemovePin':
                while self.cur_pin_south in self.pins_south: self.pins_south.remove(self.cur_pin_south) 
                #Also remove from the populate list
                self.populate = [x for x in self.populate if not (x[0] == Directions.SOUTH and x[1] == self.cur_pin_south) ]

        self.darea.queue_draw()

    def add_edit_menu_actions(self, action_group):
        action_group.add_actions([
            ("EditMenu", None, "Edit"),
            ("AddPin", None, "AddPin", None, None,
             self.on_menu_others),
            ("RemovePin", None, "RemovePin", None, None,
             self.on_menu_others),
        ])

    def on_button_press(self, w, e):
        # print 'PRESS: ', e.x, ' ', e.y
        if e.type == Gdk.EventType.BUTTON_PRESS \
                and e.button == MouseButtons.LEFT_BUTTON:
            self.BEGIN_MOUSE_X = e.x
            self.BEGIN_MOUSE_Y = e.y
        if e.type == Gdk.EventType.BUTTON_PRESS \
                and e.button == MouseButtons.RIGHT_BUTTON:
           print "Right button pressed"
           self.popup.popup(None, None, None, None, e.button, e.time)
        if e.type == Gdk.EventType._2BUTTON_PRESS:
           print "User hit Double Click"

           w = self.darea.get_allocation().width
           h = self.darea.get_allocation().height
           direction = ''
   
           if (self.MOUSE_X-w/2) >= -self.ic_width/2-10 and (self.MOUSE_X-w/2) < -self.ic_width/2-10+10 and (self.MOUSE_Y-h/2) >= -self.ic_length/2+0*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_Y-h/2) < -self.ic_length/2+self.max_pins_per_length*(self.pin_width+self.pins_distance)+5+5:
             #print "West " + str(self.cur_pin_west)       
             direction = 'West'
             if self.cur_pin_west not in self.pins_west:
                print "Do nothing [West]"
             if self.cur_pin_west in self.pins_west:
                print "Set current pin [West]"
                self.cur_pin_selected = self.cur_pin_west
                self.cur_direction = Directions.WEST
                self.Orientation = 'R'
                #Update Pin
                self.update_pin_label.set_label("<b>WEST "+str(self.cur_pin_selected)+"</b>")
                self.update_pin_label.set_use_markup(True) 
                #assign pin coordinates
                self.PIN_X = -(self.ic_width/2+self.pin_length)
                self.PIN_Y = -self.ic_length/2+self.cur_pin_selected*(self.pin_width+self.pins_distance)+5
                nom = [x for x in self.populate if(x[0]==Directions.WEST and x[1]==self.cur_pin_selected)]
                if nom:
                   self.cur_signal_name_label.set_label("<b>"+str(nom[0][2])+"</b>")
                   self.cur_signal_name_label.set_use_markup(True)
                   self.cur_pin_name_label.set_label("<b>"+str(nom[0][3])+"</b>")
                   self.cur_pin_name_label.set_use_markup(True)
                   #self.cur_orientation_label.set_label("<b>"+str(nom[0][7])+"</b>")
                   #self.cur_orientation_label.set_use_markup(True)
                   self.cur_type_label.set_label("<b>"+str(nom[0][12])+"</b>")
                   self.cur_type_label.set_use_markup(True)
                   self.cur_shape_label.set_label("<b>"+str(nom[0][13])+"</b>")
                   self.cur_shape_label.set_use_markup(True)

           if (self.MOUSE_X-w/2) >= self.ic_width/2 and (self.MOUSE_X-w/2) < self.ic_width/2+10+10 and (self.MOUSE_Y-h/2) >= -self.ic_length/2+0*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_Y-h/2) < -self.ic_length/2+self.max_pins_per_length*(self.pin_width+self.pins_distance)+5+5:
             #print "East " + str(self.cur_pin_east)
             direction = 'East'
             if self.cur_pin_east not in self.pins_east:
                print "Do nothing [East]"
             if self.cur_pin_east in self.pins_east:
                print "Set current pin [East]"
                self.cur_pin_selected = self.cur_pin_east
                self.cur_direction = Directions.EAST
                self.Orientation = 'L'
                #Update Pin
                self.update_pin_label.set_label("<b>EAST "+str(self.cur_pin_selected)+"</b>")
                self.update_pin_label.set_use_markup(True) 
                #assign pin coordinates
                self.PIN_X = self.ic_width/2+self.pin_length
                self.PIN_Y = -self.ic_length/2+self.cur_pin_selected*(self.pin_width+self.pins_distance)+5
                nom = [x for x in self.populate if(x[0]==Directions.EAST and x[1]==self.cur_pin_selected)]
                if nom:
                   self.cur_signal_name_label.set_label("<b>"+str(nom[0][2])+"</b>")
                   self.cur_signal_name_label.set_use_markup(True)
                   self.cur_pin_name_label.set_label("<b>"+str(nom[0][3])+"</b>")
                   self.cur_pin_name_label.set_use_markup(True)
                   #self.cur_orientation_label.set_label("<b>"+str(nom[0][7])+"</b>")
                   #self.cur_orientation_label.set_use_markup(True)
                   self.cur_type_label.set_label("<b>"+str(nom[0][12])+"</b>")
                   self.cur_type_label.set_use_markup(True)
                   self.cur_shape_label.set_label("<b>"+str(nom[0][13])+"</b>")
                   self.cur_shape_label.set_use_markup(True)

           if (self.MOUSE_X-w/2) >= -self.ic_width/2+0*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_X-w/2) < -self.ic_width/2+self.max_pins_per_width*(self.pin_width+self.pins_distance)+5+5 and (self.MOUSE_Y-h/2) >= -self.ic_length/2-10-10 and (self.MOUSE_Y-h/2) < -self.ic_length/2-10+10:
             direction = 'North'
             #print "North " + str(self.cur_pin_north)
             if self.cur_pin_north not in self.pins_north:
                print "Do nothing [North]"
             if self.cur_pin_north in self.pins_north:
                print "Set current pin [North]"
                self.cur_pin_selected = self.cur_pin_north
                self.cur_direction = Directions.NORTH
                self.Orientation = 'D'
                #Update Pin
                self.update_pin_label.set_label("<b>NORTH "+str(self.cur_pin_selected)+"</b>")
                self.update_pin_label.set_use_markup(True) 
                #assign pin coordinates
                self.PIN_X = -self.ic_width/2+self.cur_pin_selected*(self.pin_width+self.pins_distance)+5
                self.PIN_Y = self.ic_length/2+self.pin_length
                nom = [x for x in self.populate if(x[0]==Directions.NORTH and x[1]==self.cur_pin_selected)]
                if nom:
                   self.cur_signal_name_label.set_label("<b>"+str(nom[0][2])+"</b>")
                   self.cur_signal_name_label.set_use_markup(True)
                   self.cur_pin_name_label.set_label("<b>"+str(nom[0][3])+"</b>")
                   self.cur_pin_name_label.set_use_markup(True)
                   #self.cur_orientation_label.set_label("<b>"+str(nom[0][7])+"</b>")
                   #self.cur_orientation_label.set_use_markup(True)
                   self.cur_type_label.set_label("<b>"+str(nom[0][12])+"</b>")
                   self.cur_type_label.set_use_markup(True)
                   self.cur_shape_label.set_label("<b>"+str(nom[0][13])+"</b>")
                   self.cur_shape_label.set_use_markup(True)

           if (self.MOUSE_X-w/2) >= -self.ic_width/2+0*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_X-w/2) < -self.ic_width/2+self.max_pins_per_width*(self.pin_width+self.pins_distance)+5+5 and (self.MOUSE_Y-h/2) >= self.ic_length/2-10 and (self.MOUSE_Y-h/2) < self.ic_length/2+20:
             #print "South " + str(self.cur_pin_south)
             direction = 'South'
             if self.cur_pin_south not in self.pins_south:
                print "Do nothing [South]"
             if self.cur_pin_south in self.pins_south:
                print "Set current pin [South]"
                self.cur_pin_selected = self.cur_pin_south
                self.cur_direction = Directions.SOUTH
                self.Orientation = 'U'
                #Update Pin
                self.update_pin_label.set_label("<b>SOUTH "+str(self.cur_pin_selected)+"</b>")
                self.update_pin_label.set_use_markup(True) 
                #assign pin coordinates
                self.PIN_X = -self.ic_width/2+self.cur_pin_selected*(self.pin_width+self.pins_distance)+5
                self.PIN_Y = -(self.ic_length/2+self.pin_length)
                nom = [x for x in self.populate if(x[0]==Directions.SOUTH and x[1]==self.cur_pin_selected)]
                if nom:
                   self.cur_signal_name_label.set_label("<b>"+str(nom[0][2])+"</b>")
                   self.cur_signal_name_label.set_use_markup(True)
                   self.cur_pin_name_label.set_label("<b>"+str(nom[0][3])+"</b>")
                   self.cur_pin_name_label.set_use_markup(True)
                   #self.cur_orientation_label.set_label("<b>"+str(nom[0][7])+"</b>")
                   #self.cur_orientation_label.set_use_markup(True)
                   self.cur_type_label.set_label("<b>"+str(nom[0][12])+"</b>")
                   self.cur_type_label.set_use_markup(True)
                   self.cur_shape_label.set_label("<b>"+str(nom[0][13])+"</b>")
                   self.cur_shape_label.set_use_markup(True)

        #print self.PIN_X
        #print self.PIN_Y

        self.darea.queue_draw()

    def on_button_release(self, w, e):
        # print 'RELEASE: ',e.x, ' ', e.y
        if e.type == Gdk.EventType.BUTTON_RELEASE \
                and e.button == MouseButtons.LEFT_BUTTON:
            self.END_MOUSE_X = e.x
            self.END_MOUSE_Y = e.y
        self.darea.queue_draw()

    def on_motion_notify_event(self, w, e):
        # print 'MOVING: ',e.x, ' ', e.y
        if e.type == Gdk.EventType.MOTION_NOTIFY:
            self.MOUSE_X = e.x
            self.MOUSE_Y = e.y
        # print 'MOUSE: ',self.MOUSE_X, ' ', self.MOUSE_Y
        self.darea.queue_draw()

    def signal_handler(self, signum, frame):
        print("signal received ", signum, frame)

    def on_draw(self, wid, cr):

        #intialize self.RESULT each time
        self.RESULT = ''

        self.action_group.get_action("AddPin").set_sensitive(False)
        self.action_group.get_action("RemovePin").set_sensitive(False)

        cr.select_font_face("Times New Roman", cairo.FONT_SLANT_NORMAL, 
            cairo.FONT_WEIGHT_NORMAL)

        cr.set_line_width(4)
        #w, h = self.darea.get_size()
        w = self.darea.get_allocation().width
        h = self.darea.get_allocation().height

        # Origin X,Y in the center
        cr.translate(w / 2, h / 2)

        cr.set_source_rgb(0.5, 0.2, 0.7)
        cr.rectangle(
            -self.ic_width / 2, -self.ic_length / 2, self.ic_width, self.ic_length)
        cr.stroke()
        cr.set_line_width(1)

        # Can we populate the total pins along the perimeter?
        perimeter = 2 * (self.ic_width + self.ic_length)

        # assume pin width = 5 and gap between pins = 5
        self.max_pins_per_width = self.ic_width / (self.pin_width+self.pins_distance)
        self.max_pins_per_length = self.ic_length / (self.pin_width+self.pins_distance)

        # Max pins that can be drawn sanely
        max_pins = 0
        if (self.sides == 2):
            max_pins = 2 * (self.max_pins_per_length)
        elif (self.sides == 4):
            max_pins = 2 * (self.max_pins_per_width + self.max_pins_per_length)

        self.total_pins = max_pins

        # Draw markers

        # Markers on West
        for i in range(self.max_pins_per_length):
            if (self.MOUSE_X-w/2) >= -self.ic_width/2-10 and (self.MOUSE_X-w/2) < -self.ic_width/2-10+10 and (self.MOUSE_Y-h/2) >= -self.ic_length/2+i*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_Y-h/2) < -self.ic_length/2+i*(self.pin_width+self.pins_distance)+5+5:
                self.cur_pin_west = i       
                cr.set_source_rgb(0.5, 0.2, 0.7)
                #Highlight selected pin in blue
                if self.cur_pin_selected == i and self.cur_direction == Directions.WEST:
                   cr.set_source_rgb(0.0, 0.0, 1.0)
                   cr.show_text("Selected Pin [West] "+str(i))
                cr.move_to(-self.ic_width/2-10-40, -self.ic_length/2+i*(self.pin_width+self.pins_distance)+5)
                cr.show_text("West "+str(i))
                # Now show the options to add pin or remove pin
                if i in self.pins_west:
                   self.action_group.get_action("AddPin").set_sensitive(False)
                   self.action_group.get_action("RemovePin").set_sensitive(True)
                else: 
                   self.action_group.get_action("AddPin").set_sensitive(True)
                   self.action_group.get_action("RemovePin").set_sensitive(False)
            else:
                cr.set_source_rgb(1, 0.3, 0.9)
            cr.rectangle(-self.ic_width/2-10 , -self.ic_length/2+i*(self.pin_width+self.pins_distance)+5, 10, 1)
            cr.fill()   
        for i in range(len(self.pins_west)):
            #print self.pins_west[i]
            cr.rectangle(-self.ic_width/2-20 , -self.ic_length/2+self.pins_west[i]*(self.pin_width+self.pins_distance)+5, 20, 1)
            cr.fill()   
            nom = [x for x in self.populate if(x[0]==Directions.WEST and x[1]==self.pins_west[i])]
            # naming outside IC border
            if not nom:
               cr.move_to(-self.ic_width/2-20-80 , -self.ic_length/2+self.pins_west[i]*(self.pin_width+self.pins_distance)+5)
               cr.show_text("West OUT"+str(self.pins_west[i]))
            else:
               cr.move_to(-self.ic_width/2-len(nom[0][2])*5 , -self.ic_length/2+self.pins_west[i]*(self.pin_width+self.pins_distance)+5)
               cr.show_text(str(nom[0][2]))
            # naming inside IC border
            if not nom:
               cr.move_to(-self.ic_width/2-20+20+5 , -self.ic_length/2+self.pins_west[i]*(self.pin_width+self.pins_distance)+5)
               cr.show_text("West IN"+str(self.pins_west[i]))
            else:
               cr.move_to(-self.ic_width/2+5 , -self.ic_length/2+self.pins_west[i]*(self.pin_width+self.pins_distance)+5)
               cr.show_text(str(nom[0][3]))
               

        # Markers on East
        for i in range(self.max_pins_per_length):
            if (self.MOUSE_X-w/2) >= self.ic_width/2 and (self.MOUSE_X-w/2) < self.ic_width/2+10+10 and (self.MOUSE_Y-h/2) >= -self.ic_length/2+i*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_Y-h/2) < -self.ic_length/2+i*(self.pin_width+self.pins_distance)+5+5:
                self.cur_pin_east = i       
                cr.set_source_rgb(0.5, 0.2, 0.7)
                #Highlight selected pin in blue
                if self.cur_pin_selected == i and self.cur_direction == Directions.EAST:
                   cr.set_source_rgb(0.0, 0.0, 1.0)
                   cr.show_text("Selected Pin [East] "+str(i))
                cr.move_to(self.ic_width/2-10+40, -self.ic_length/2+i*(self.pin_width+self.pins_distance)+5)
                cr.show_text("East "+str(i))
                # Now show the options to add pin or remove pin
                if i in self.pins_east:
                   self.action_group.get_action("AddPin").set_sensitive(False)
                   self.action_group.get_action("RemovePin").set_sensitive(True)
                else: 
                   self.action_group.get_action("AddPin").set_sensitive(True)
                   self.action_group.get_action("RemovePin").set_sensitive(False)
            else:
                cr.set_source_rgb(1, 0.3, 0.9)
            cr.rectangle(self.ic_width/2 , -self.ic_length/2+i*(self.pin_width+self.pins_distance)+5, 10, 1)
            cr.fill()   
        for i in range(len(self.pins_east)):
            #print self.pins_east[i]
            cr.rectangle(self.ic_width/2 , -self.ic_length/2+self.pins_east[i]*(self.pin_width+self.pins_distance)+5, 20, 1)
            cr.fill()   
            nom = [x for x in self.populate if(x[0]==Directions.EAST and x[1]==self.pins_east[i])]
            # naming outside IC border
            if not nom:
               cr.move_to(self.ic_width/2+40 , -self.ic_length/2+self.pins_east[i]*(self.pin_width+self.pins_distance)+5)
               cr.show_text("East OUT"+str(self.pins_east[i]))
            else:
               cr.move_to(self.ic_width/2+5 , -self.ic_length/2+self.pins_east[i]*(self.pin_width+self.pins_distance)+5)
               cr.show_text(str(nom[0][2]))
            # naming inside IC border
            if not nom:
               cr.move_to(self.ic_width/2-40 , -self.ic_length/2+self.pins_east[i]*(self.pin_width+self.pins_distance)+5)
               cr.show_text("East IN "+str(self.pins_east[i]))
            else:
               cr.move_to(self.ic_width/2-len(nom[0][3])*5 , -self.ic_length/2+self.pins_east[i]*(self.pin_width+self.pins_distance)+5)
               cr.show_text(str(nom[0][3]))

        # Markers on North
        for i in range(self.max_pins_per_width):
            if (self.MOUSE_X-w/2) >= -self.ic_width/2+i*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_X-w/2) < -self.ic_width/2+i*(self.pin_width+self.pins_distance)+5+5 and (self.MOUSE_Y-h/2) >= -self.ic_length/2-10-10 and (self.MOUSE_Y-h/2) < -self.ic_length/2-10+10:
                self.cur_pin_north = i       
                cr.set_source_rgb(0.5, 0.2, 0.7)
                #Highlight selected pin in blue
                if self.cur_pin_selected == i and self.cur_direction == Directions.NORTH:
                   cr.set_source_rgb(0.0, 0.0, 1.0)
                   cr.show_text("Selected Pin [North] "+str(i))
                cr.move_to(-self.ic_width/2+i*(self.pin_width+self.pins_distance)+5, -self.ic_length/2-10-20)
                #show vertical text
                cr.rotate(-math.pi/2)
                cr.show_text("North "+str(i))
                cr.rotate(math.pi/2)
                # Now show the options to add pin or remove pin
                if i in self.pins_north:
                   self.action_group.get_action("AddPin").set_sensitive(False)
                   self.action_group.get_action("RemovePin").set_sensitive(True)
                else: 
                   self.action_group.get_action("AddPin").set_sensitive(True)
                   self.action_group.get_action("RemovePin").set_sensitive(False)
            else:
                cr.set_source_rgb(1, 0.3, 0.9)
            cr.rectangle(-self.ic_width/2+i*(self.pin_width+self.pins_distance)+5 , -self.ic_length/2-10, 1, 10)
            cr.fill()   
        for i in range(len(self.pins_north)):
            #print self.pins_north[i]
            cr.rectangle(-self.ic_width/2+self.pins_north[i]*(self.pin_width+self.pins_distance)+5 , -self.ic_length/2-10-20, 1, 20)
            cr.fill()   
            nom = [x for x in self.populate if(x[0]==Directions.NORTH and x[1]==self.pins_north[i])]
            # naming outside IC border
            if not nom:
               cr.move_to(-self.ic_width/2+self.pins_north[i]*(self.pin_width+self.pins_distance)+5 , -self.ic_length/2-10-20-5)
               #show vertical text
               cr.rotate(-math.pi/2)
               cr.show_text("North OUT"+str(self.pins_north[i]))
               cr.rotate(math.pi/2)
            else:
               cr.move_to(-self.ic_width/2+self.pins_north[i]*(self.pin_width+self.pins_distance)+5 , -self.ic_length/2-10-5)
               #show vertical text
               cr.rotate(-math.pi/2)
               cr.show_text(str(nom[0][2]))
               cr.rotate(math.pi/2)
            # naming inside IC border
            if not nom:
               cr.move_to(-self.ic_width/2+self.pins_north[i]*(self.pin_width+self.pins_distance)+5 , -self.ic_length/2-10-20+80)
               #show vertical text
               cr.rotate(-math.pi/2)
               cr.show_text("North IN "+str(self.pins_north[i]))
               cr.rotate(math.pi/2)
            else:
               cr.move_to(-self.ic_width/2+self.pins_north[i]*(self.pin_width+self.pins_distance)+5 , -self.ic_length/2-10+len(nom[0][3])*5)
               #show vertical text
               cr.rotate(-math.pi/2)
               cr.show_text(str(nom[0][3]))
               cr.rotate(math.pi/2)

        # Markers on South
        for i in range(self.max_pins_per_width):
            if (self.MOUSE_X-w/2) >= -self.ic_width/2+i*(self.pin_width+self.pins_distance)+5 and (self.MOUSE_X-w/2) < -self.ic_width/2+i*(self.pin_width+self.pins_distance)+5+5 and (self.MOUSE_Y-h/2) >= self.ic_length/2-10 and (self.MOUSE_Y-h/2) < self.ic_length/2+20:
                self.cur_pin_south = i       
                cr.set_source_rgb(0.5, 0.2, 0.7)
                #Highlight selected pin in blue
                if self.cur_pin_selected == i and self.cur_direction == Directions.SOUTH:
                   cr.set_source_rgb(0.0, 0.0, 1.0)
                   cr.show_text("Selected Pin [South] "+str(i))
                cr.move_to(-self.ic_width/2+i*(self.pin_width+self.pins_distance)+5, self.ic_length/2-10+60)
                #show vertical text
                cr.rotate(-math.pi/2)
                cr.show_text("South "+str(i))
                cr.rotate(math.pi/2)
                # Now show the options to add pin or remove pin
                if i in self.pins_south:
                   self.action_group.get_action("AddPin").set_sensitive(False)
                   self.action_group.get_action("RemovePin").set_sensitive(True)
                else: 
                   self.action_group.get_action("AddPin").set_sensitive(True)
                   self.action_group.get_action("RemovePin").set_sensitive(False)
            else:
                cr.set_source_rgb(1, 0.3, 0.9)
            cr.rectangle(-self.ic_width/2+i*(self.pin_width+self.pins_distance)+5 , self.ic_length/2, 1, 10)
            cr.fill()   
        for i in range(len(self.pins_south)):
            #print self.pins_south[i]
            cr.rectangle(-self.ic_width/2+self.pins_south[i]*(self.pin_width+self.pins_distance)+5 , self.ic_length/2, 1, 20)
            cr.fill()   
            nom = [x for x in self.populate if(x[0]==Directions.SOUTH and x[1]==self.pins_south[i])]
            # naming outside IC border
            if not nom:
               cr.move_to(-self.ic_width/2+self.pins_south[i]*(self.pin_width+self.pins_distance)+5 , self.ic_length/2+80)
               #show vertical text
               cr.rotate(-math.pi/2)
               cr.show_text("South OUT"+str(self.pins_south[i]))
               cr.rotate(math.pi/2)
            else:
               cr.move_to(-self.ic_width/2+self.pins_south[i]*(self.pin_width+self.pins_distance)+5 , self.ic_length/2+len(nom[0][2])*5)
               #show vertical text
               cr.rotate(-math.pi/2)
               cr.show_text(str(nom[0][2]))
               cr.rotate(math.pi/2)              
            # naming inside IC border
            if not nom:
               cr.move_to(-self.ic_width/2+self.pins_south[i]*(self.pin_width+self.pins_distance)+5 , self.ic_length/2-5)
               #show vertical text
               cr.rotate(-math.pi/2)
               cr.show_text("South IN "+str(self.pins_south[i]))
               cr.rotate(math.pi/2)
            else:
               cr.move_to(-self.ic_width/2+self.pins_south[i]*(self.pin_width+self.pins_distance)+5 , self.ic_length/2-5)
               #show vertical text
               cr.rotate(-math.pi/2)
               cr.show_text(str(nom[0][3]))
               cr.rotate(math.pi/2)

 
        if self.crosshair == True:
           #Move origin back to top left
           cr.translate(-w / 2, -h / 2)
           cr.set_source_rgb(0.5, 0.5, 0.5)
           cr.move_to(self.MOUSE_X, self.MOUSE_Y+2*h)
           cr.line_to(self.MOUSE_X, self.MOUSE_Y-h)
           cr.stroke()
           cr.line_to(self.MOUSE_X+2*w, self.MOUSE_Y)
           cr.line_to(self.MOUSE_X-w, self.MOUSE_Y)
           cr.stroke()
           #Move origin back to center
           cr.translate(w / 2, h / 2)

        cr.set_source_rgb(1, 0.3, 0.9)
        for i in range(len(self.populate)):
            print self.populate[i]

        # Get the current date and time
        cur_time = strftime("%d/%m/%Y-%H:%M:%S", gmtime())
        #Now form the Library Component
        self.RESULT += "EESchema-LIBRARY Version 2.3  Date: " + str(cur_time) + "\n" 
        self.RESULT += "#" + "\n" 
        self.RESULT += "# "+ self.ic_name_entry.get_text() + "\n" 
        self.RESULT += "#" + "\n" 
        self.RESULT += "DEF " + self.ic_name_entry.get_text() + " U 0 40 Y Y 1 0 N" + "\n" 
        self.RESULT += "F0 \"U\" 0 -100 50 H V C C" + "\n" 
        self.RESULT += "F1 \"" + self.ic_name_entry.get_text() + "\" 0 100 50 H V C C" + "\n" 
        self.RESULT += "F2 \"MODULE\" 0 0 50 H I C C" + "\n" 
        self.RESULT += "F3 \"DOCUMENTATION\" 0 0 50 H I C C" + "\n" 
        self.RESULT += "#ALIAS " + self.ic_name_entry.get_text() + "\n"
        self.RESULT += "$FPLIST" + "\n"
        self.RESULT += " # Enter all the allowed Foot Prints here - one on each line" + "\n"
        self.RESULT += "$ENDFPLIST" + "\n"
        self.RESULT += "DRAW" + "\n"
        self.RESULT += "S -" + str(self.ic_width/2) + " -" + str(self.ic_length/2) + " "+ str(self.ic_width/2) +" " + str(self.ic_length/2) +" 1 0 0 N" + "\n"
        for j in self.populate:
            self.RESULT += "X "+str(j[2])+" "+str(j[3])+" "+str(j[4])+" "+str(j[5])+" "+str(j[6])+" "+str(j[7])+" "+str(j[8])+" "+str(j[9])+" "+str(j[10])+" "+str(j[11])+" "+str(j[12])+" "+str(j[13])+"\n"
        self.RESULT += "ENDDRAW" + "\n"
        self.RESULT += "ENDDEF" + "\n"
        self.RESULT += "#" + "\n"
        self.RESULT += "#End Library" + "\n"
        #print self.RESULT

def main():

    app = UKLCIG()
    Gtk.main()


if __name__ == "__main__":
    main()
