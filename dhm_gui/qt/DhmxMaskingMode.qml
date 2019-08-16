import QtQuick 2.4
import QtQuick.Controls 1.3
import QtGraphicalEffects 1.0

Item {
    id: mask
    visible: true
    signal mask_pos(int mask_no, double radius, int x, int y)
    signal remove_mask(int mask_no)
    property var wavelength1: undefined
    property var wavelength2: undefined
    property var wavelength3: undefined

    property int max_wavelength: 0
    property int wavelength_ct: 0
    property double zoom_amnt: 0.3105
    /* This property does not change */
    property double zoom_initial: -1.00

    property string display_mask_path: ""

    /* Previous frame width and height to get exact pixel differences for mask placement */
    property int width_prev: 000
    property int height_prev: 000

    property int w1_prev_width: 000
    property int w1_prev_height: 000

    property int w2_prev_width: 000
    property int w2_prev_height: 000

    property int w3_prev_width: 000
    property int w3_prev_height: 000
    onVisibleChanged: {

        if(!visible){
            width_prev = width
            height_prev = height
            if(wavelength1){
               w1_prev_width = wavelength1.width
               w1_prev_height = wavelength1.height
            }
            if(wavelength2){
               w2_prev_width = wavelength2.width
               w2_prev_height = wavelength2.height
            }
            if(wavelength3){
               w3_prev_width = wavelength3.width
               w3_prev_height = wavelength3.height
            }
        }
    }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onClicked: {
                if(!wavelength1 && max_wavelength >= 1){
                  wavelength1 = selectionComponent.createObject(parent, {"x": mouseX-((parent.width/3)/2), "y": mouseY-((parent.height/3)/2), "width": parent.width / 3, "height": parent.width / 3, "name": "Wavelength 1", "mask_num":1})
                  updateCenter(wavelength1.mask_num,mouseX-((parent.width/3)/2),mouseY-((parent.height/3)/2),parent.width / 3,parent.width / 3)
                }
                else if(!wavelength2 && max_wavelength >= 2){
                  wavelength2 = selectionComponent.createObject(parent, {"x":  mouseX-((parent.width/3)/2), "y": mouseY-((parent.height/3)/2), "width": parent.width / 3, "height": parent.width / 3, "name": "Wavelength 2","mask_num":2})
                  updateCenter(wavelength2.mask_num,mouseX-((parent.width/3)/2),mouseY-((parent.height/3)/2),parent.width / 3,parent.width / 3)
                }
                else if(!wavelength3 && max_wavelength >= 3){
                  wavelength3 = selectionComponent.createObject(parent, {"x": mouseX-((parent.width/3)/2), "y": mouseY-((parent.height/3)/2), "width": parent.width / 3, "height": parent.width / 3, "name": "Wavelength 3","mask_num":3})
                  updateCenter(wavelength3.mask_num,mouseX-((parent.width/3)/2),mouseY-((parent.height/3)/2),parent.width / 3,parent.width / 3)
                }
            }
        }

   Rectangle{
       id: center_point_1
       visible: false
       x:250
       y:250
       width:3
       height:3
   }
   Rectangle{
       id: center_point_2
       visible: false
       x:250
       y:250
       width:3
       height:3
   }
   Rectangle{
       id: center_point_3
       visible: false
       x:250
       y:250
       width:3
       height:3
   }

   /* The dark shade overlay used for masking */
   Image{
       id:image_display_mask
       anchors.fill:parent
       opacity: 0.7
       cache: false
   }



    Component {
        id: selectionComponent
        Rectangle {
            id: selComp
            property int mask_num: 0

            anchors.centerIn: center_point_1
            radius: width*0.5 //to create a circle

            border {
                width: 2
                color: "steelblue"
            }
            color: "#004682B4"
            //color: "white"

            property int rulersSize: 15
            property string name: "Wavelength"
            property double r: (selComp.width/2) * (1/zoom_amnt)
            property double r_actual: (selComp_ref.width/2) * (1/zoom_initial)
            property int position_x: (selComp.x + (selComp.width/2))/zoom_amnt
            property int position_y: (selComp.y + (selComp.height/2))/zoom_amnt
            property int wavelength_width: selComp.width
            property int wavelength_height: selComp.height

            /* This rectangle is used as a reference for width/height/radius when zooming in/out */
            Rectangle{
                id:selComp_ref
                anchors.centerIn: parent
                visible: false
                Component.onCompleted: {
                    width = selComp.width
                    height = selComp.height
                    radius = width *0.5
                }

            }

            /* RETICULE */
            Item{
                id: reticule
                x: selComp.width / 2
                y: selComp.height / 2
                Rectangle{
                    id: ret_x_axis
                    color: "steelblue"
                    x: -width/2
                    y: -height/2

                    width: 10
                    height: 2

                    opacity: 0.4
                }
                Rectangle{
                    id: ret_y_axis
                    color: "steelblue"
                    y: -height/2
                    x: -width/2
                    width: 2
                    height: 10

                    opacity: 0.4
                }
            }

            /* X,Y, RADIUS INFO */
            Item{
                id: info
                x: selComp.width
                y: selComp.height/2

                Rectangle{
                    id: uix_1
                    width:40
                    height:1
                    color: "steelblue"

                    Rectangle{
                        id: uix_2
                        width:60
                        height:1
                        x: parent.width - 10
                        y: -20
                        rotation: -45
                        color: "steelblue"

                        Item{
                            id: info_text
                            rotation: 45
                            x: parent.width + 20 // for asthetics
                            y: parent.height - 10 // for asthetics

                            Label{
                                id: label_wl_
                                text: selComp.name
                                font.bold: true
                                color: "white"
                                opacity: 0.6

                            }
                            Label{
                                id: label_r
                                text: "Radius: "+selComp.r_actual
                                font.bold: true
                                color: "white"
                                opacity: 0.6
                                y: label_wl_.font.pixelSize + 3
                            }
                            Label{
                                id: label_x
                                text: "x: "+selComp.position_x
                                font.bold: true
                                color: "white"
                                opacity: 0.6
                                y: label_r.y + label_r.font.pixelSize + 3
                            }
                            Label{
                                id: label_y
                                text: "y: "+selComp.position_y
                                font.bold: true
                                color: "white"
                                opacity: 0.6
                                y: label_x.y + label_x.font.pixelSize + 3
                            }
                        }

                    }
                }

                states: [
                    State { name: "visible";
                        PropertyChanges { target: info; opacity: 1.0}
                    },
                    State { name: "invisible";
                        PropertyChanges { target: info; opacity: 0.0}
                    }
                ]
                transitions: Transition{
                    NumberAnimation {property: "opacity"; duration: 500}
                }
                function flip_info(status){
                    if(status){
                        info.x = -uix_1.width
                        uix_2.x = -uix_1.width - 10
                        uix_2.rotation = 45
                        info_text.rotation = -45
                        info_text.x = -80 // for asthetics
                        info_text.y = -10 // for asthetics
                    }
                    else{
                        info.x = selComp.width
                        uix_2.x = uix_1.width - 10
                        uix_2.rotation = -45
                        info_text.rotation = 45
                        info_text.x = uix_2.width + 20 // for asthetics
                        info_text.y = uix_2.height - 10 // for asthetics
                    }
                }
            }

            /* This is the dragging component of the selection mask */
            MouseArea {     // drag mouse area
                anchors.fill: parent
                hoverEnabled: true
                id: draggable
                drag{

                    target: center_point_1
                    minimumX: 0
                    minimumY: 0
                    maximumX: parent.parent.width
                    maximumY: parent.parent.height
                    smoothed: true
                }

                /* This timer was designed to update the shadow masks and is used only when
                 * the user initially starts the masking mode.  Since Qt does not receive
                 * the positional change immedietly due to the Qt engine, this is called
                 * to constantly update the positional values of hte masks until the user
                 * moves their mouse and forces an update */
                Timer{
                    id: timer_shadow_mask
                    interval: 60
                    running: true
                    repeat: true
                    onTriggered: {
                        if(wavelength1){
                            mask_pos(1,wavelength1.r,wavelength1.position_x,wavelength1.position_y)
                        }
                        if(wavelength2){
                             mask_pos(2,wavelength2.r,wavelength2.position_x,wavelength2.position_y)
                        }
                        if(wavelength3){
                             mask_pos(3,wavelength3.r,wavelength3.position_x,wavelength3.position_y)
                        }
                    }
                }

                /* When the visiblity is changed to true, fire the timer to update the canvas */
                onVisibleChanged: {
                    if(visible)
                       timer_shadow_mask.running = true
                    if(!visible)
                        timer_shadow_mask.running = false
                }

                /* Either mouseX or MouseY could be used.  MouseX was chosen arbitrarily.
                 * This will update the info position of each mask with each pixel movement
                 * and will also send masking positions to dhmx.py to update PIL(low)*/
                onMouseXChanged: {
                    timer_shadow_mask.running = false
                    /* 500 pixels is used to compensate for the width of the text as
                     * there is no direct way to access how much width the text consumes */
                    /* TODO: Find a better solution instead of a "magic number" */
                    if(position_x + (selComp.width*2) + 500 >(mask.width/zoom_amnt))
                       info.flip_info(true)
                    else
                       info.flip_info(false)

                    /* Emit a signal of each individual wavelength that has been enabled to tell
                     * Python to create a mask using PIL(low) so that the user can see what is
                     * being masked off */
                    if(wavelength1){
                        mask_pos(1,wavelength1.r,wavelength1.position_x,wavelength1.position_y)
                    }
                    if(wavelength2){
                         mask_pos(2,wavelength2.r,wavelength2.position_x,wavelength2.position_y)
                    }
                    if(wavelength3){
                         mask_pos(3,wavelength3.r,wavelength3.position_x,wavelength3.position_y)
                    }
                }

                onDoubleClicked: {
                    if(parent.name == "Wavelength 1")
                       remove_mask(1)
                       mask_pos(-1,0,0,0) //throw in an invalid mask position to update the function
                    if(parent.name == "Wavelength 2")
                       remove_mask(2)
                       mask_pos(-1,0,0,0) //throw in an invalid mask position to update the function
                    if(parent.name == "Wavelength 3")
                       remove_mask(3)
                       mask_pos(-1,0,0,0) //throw in an invalid mask position to update the function
                    parent.destroy()        // destroy component
                }

                onEntered: {
                    /* 500 pixels is used to compensate for the width of the text as
                     * there is no direct way to access how much width the text consumes */
                    /* TODO: Find a better solution instead of a "magic number" */
                    if(position_x + (selComp.width*2) + 500 >(mask.width/zoom_amnt))
                       info.flip_info(true)
                    else
                       info.flip_info(false)
                    info.state = "visible"
                }
                onExited: {
                    info.state = "invisible"
                }
            }

            Rectangle {
                width: rulersSize
                height: rulersSize
                radius: rulersSize
                color: "steelblue"
                anchors.horizontalCenter: parent.left
                anchors.verticalCenter: parent.verticalCenter

                MouseArea {
                    anchors.fill: parent
                    drag{ target: parent; axis: Drag.XAxis }
                    onMouseXChanged: {
                        if(drag.active){
                            selComp_ref.width = selComp_ref.width - mouseX
                            selComp_ref.height = selComp_ref.height - mouseX

                            selComp.width = selComp.width - mouseX
                            //selComp.x = selComp.width + mouseX
                            selComp.height = selComp.height - mouseX
                            selComp.x = selComp.x + mouseX
                            if(selComp.width < 30)
                                selComp.width = 30
                        }
                    }
                }
            }

            Rectangle {
                width: rulersSize
                height: rulersSize
                radius: rulersSize
                color: "steelblue"
                anchors.horizontalCenter: parent.right
                anchors.verticalCenter: parent.verticalCenter

                MouseArea {
                    anchors.fill: parent
                    drag{ target: parent; axis: Drag.XAxis }
                    onMouseXChanged: {
                        if(drag.active){
                            selComp_ref.width = selComp_ref.width + mouseX
                            selComp_ref.height = selComp_ref.height + mouseX

                            selComp.width = selComp.width + mouseX
                            selComp.height = selComp.height + mouseX
                            if(selComp.width < 50)
                                selComp.width = 50
                        }
                    }
                }
            }

            Rectangle {
                width: rulersSize
                height: rulersSize
                radius: rulersSize
                x: parent.x / 2
                y: 0
                color: "steelblue"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.top

                MouseArea {
                    anchors.fill: parent
                    drag{ target: parent; axis: Drag.YAxis }
                    onMouseYChanged: {
                        if(drag.active){
                            selComp_ref.width = selComp_ref.width - mouseY
                            selComp_ref.height = selComp_ref.height - mouseY

                            selComp.height = selComp.height - mouseY
                            selComp.width = selComp.width - mouseY
                            selComp.y = selComp.y + mouseY
                            if(selComp.height < 50)
                                selComp.height = 50
                        }
                    }
                }
            }


            Rectangle {
                width: rulersSize
                height: rulersSize
                radius: rulersSize
                x: parent.x / 2
                y: parent.y
                color: "steelblue"
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.bottom

                MouseArea {
                    anchors.fill: parent
                    drag{ target: parent; axis: Drag.YAxis }
                    onMouseYChanged: {
                        if(drag.active){
                            selComp_ref.width = selComp_ref.width + mouseY
                            selComp_ref.height = selComp_ref.height + mouseY

                            selComp.height = selComp.height + mouseY
                            selComp.width = selComp.width + mouseY
                            if(selComp.height < 50)
                                selComp.height = 50
                        }
                    }
                }
            }
            Component.onCompleted: {
                if(mask_num == 1){
                   selComp.anchors.centerIn = center_point_1
                   draggable.drag.target = center_point_1
                }
                if(mask_num == 2){
                   selComp.anchors.centerIn = center_point_2
                   draggable.drag.target = center_point_2
                }
                if(mask_num == 3){
                   selComp.anchors.centerIn = center_point_3
                   draggable.drag.target = center_point_3
                }
            }
        }
    }

    function set_initial_zoom(zoom){
        if(zoom_initial == -1.00){
            zoom_initial = zoom
        }
    }

    function updateCenter(masking_number,x,y,width,height){
        if(masking_number == 1){
           center_point_1.x = x + width/2
           center_point_1.y = y + height/2
        }
        if(masking_number == 2){
           center_point_2.x = x + width/2
           center_point_2.y = y + height/2
        }
        if(masking_number == 3){
           center_point_3.x = x + width/2
           center_point_3.y = y + height/2
        }
    }
    function update_display_mask(path){
        display_mask_path = path
        image_display_mask.source = display_mask_path
    }

    function update_all_positions(){
        if(wavelength1){
           wavelength1.width = wavelength1.width + (width - width_prev)
           wavelength1.height = wavelength1.height + (height - height_prev)
           center_point_1.x = center_point_1.x + (width - width_prev) - (wavelength1.width/2 - w1_prev_width/2)
           center_point_1.y = center_point_1.y + (height - height_prev) - (wavelength1.height/2 - w1_prev_height/2)
        }
        if(wavelength2){
           wavelength2.width = wavelength2.width + (width - width_prev)
           wavelength2.height = wavelength2.height + (height - height_prev)
           center_point_2.x = center_point_2.x + (width - width_prev) - (wavelength2.width/2 - w2_prev_width/2)
           center_point_2.y = center_point_2.y + (height - height_prev) - (wavelength2.height/2 - w2_prev_height/2)
        }
        if(wavelength3){
           wavelength3.width = wavelength3.width + (width - width_prev)
           wavelength3.height = wavelength3.height + (height - height_prev)
           center_point_3.x = center_point_3.x + (width - width_prev) - (wavelength3.width/2 - w3_prev_width/2)
           center_point_3.y = center_point_3.y + (height - height_prev) - (wavelength3.height/2 - w3_prev_height/2)
        }
    }
}

