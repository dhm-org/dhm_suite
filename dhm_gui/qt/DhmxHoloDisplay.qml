import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3


MouseArea {
    id: dhmx_holo_disp
    objectName: "dhmx_holo_disp"
    visible: true
    width: 700
    height: 900
    drag.target: dhmx_holo_disp
    transformOrigin: Item.TopLeft
    property int prev_mouse_pos_x: 0
    property int sample_width: sample.width
    property int sample_height: sample.height

    property string image_name: "images/please_wait.png"
    property double zoom_f: 0.0000
    property string zoom_amnt: "100%"
    property bool startup_delay: true

    property int max_wavelength: 0
    property int max_prop_dist: 0

    //The string that will be used to send the fourier command
    property string fourier_mask_cmd: ""

    //The start width and height of the frame and the source
    //the start width is always less than the source as it is length of hte display window
    property int start_width: 0 //the scaled width of the display
    property int start_height: 0 //the scaled height of the display
    property int source_width: 0 //the original source width from the camera
    property int source_height: 0 //the original source height from the camera
    property double aspect_ratio: 0.00 //the aspect ration of n*m or n*n
    property int frame_width: 636 //the display window width
    property int frame_height: 636 //the display window height

    onWidthChanged: {
        reset_view()
    }

    Rectangle {
        id: bg
        height: 800
        anchors.fill: parent
        color: "#c1bebe"
        radius: 0
        anchors.rightMargin: 0
        anchors.bottomMargin: 2
        anchors.leftMargin: 0
        anchors.topMargin: -2
        border.color: "#242424"
        border.width: 4

        states: [
            State { name: "normal";
                PropertyChanges { target: bg; color: "#c1bebe"}
            },
            State { name: "masking";
                PropertyChanges { target: bg; color: "#807a7a"}
            }
        ]
        transitions: Transition{
            PropertyAnimation {property: "color"; duration: 1000}
        }

        ComboBox {
            id: combo_disp
            x: 526
            y: 17
            width: 143
            height: 40
            visible: false

            /* 2018-12-05: disabling the use of the dropdown menu.  The way the windows are
            *  constructed in PyQt makes it difficult to dynamically switch between modes.
            *  Typically when a window is constructed, it is done in a static way and
            *  inherits the variables and functions of that window.  By switching to-and-from
            *  a window that requires and not requiring reconstruction may not be possible
            */
            enabled: false

            model: ListModel{
                id: model_disp
                ListElement{
                    text: "Hologram"
                }
                ListElement{
                    text: "Phase"
                }
                ListElement{
                    text: "Amplitude"
                }
                ListElement{
                    text: "Intensity"
                }
                ListElement{
                    text: "Fourier"
                }

            }
            onCurrentIndexChanged: {
                /* Hologram */
                if(currentIndex == 0){
                    reconst.state = "invisible"
                    button_mask.enabled = false
                }

                /* Phase, Amplitude and Intensity */
                if(currentIndex == 1 || currentIndex == 2 || currentIndex == 3){
                    reconst.state = "visible"
                    button_mask.enabled = false
                }

                /* Fourier */
                if(currentIndex == 4){
                    reconst.state = "invisible"
                    button_mask.enabled = true
                }
            }
        }

        /* Scaling handle */
        Button{
            id: button_resize
            x: 667
            y: 867
            width: 25
            height :25
            display: AbstractButton.IconOnly
            icon.source: "images/ui_handle.png"

            MouseArea{
                anchors.fill: parent
                property var cur_mouse_pos
                property var prev_mouse_pos_x: 0
                onPressed: {
                    cur_mouse_pos = mouse.x
                }

                onPositionChanged: {
                    cur_mouse_pos = mouse.x
                    cur_mouse_pos = cur_mouse_pos - prev_mouse_pos_x
                    prev_mouse_pos_x = mouse.x
                    dhmx_holo_disp.scale += cur_mouse_pos / 1024
                }
            }
        }

        Button {
            signal qml_signal_enable_historgram(bool enabled)
            objectName: "button_histogram"
            id: button_histogram
            x: 625
            y: 17
            width: 44
            height: 40
            text: qsTr("Histogram")
            icon.name: "Histogram"
            icon.source: "images/icon_histogram.png"
            icon.width: 256
            icon.height: 256
            ToolTip.visible: hovered
            ToolTip.text: "Launch the histogram window to help calibrate the microscope"
            display: AbstractButton.IconOnly

            onClicked: {
                if(subwin_histogram.state == "visible"){
                    subwin_histogram.state = "invisible"
                    subwin_histogram.enabled = false
                    qml_signal_enable_historgram(false)
                }
                else{
                    subwin_histogram.state = "visible"
                    subwin_histogram.enabled = false
                    qml_signal_enable_historgram(true)
                }

            }
        }


        Button {
            id: button_mask
            x: 564
            y: 17
            width: 44
            height: 40
            text: qsTr("Fourier Mask")
            focusPolicy: Qt.StrongFocus
            highlighted: false
            display: AbstractButton.IconOnly
            icon.height: 256
            icon.width: 256
            ToolTip.text: "Launch the fourier mask view."
            icon.name: "Masking Mode"
            icon.source: "images/icon_mask.png"

            onClicked: {
                if(!highlighted){
                    activate_mask_mode()
                    highlighted = true
                    button_apply.enabled = true
                    button_load.enabled = true
                    button_save.enabled = true
                    bg.state = "masking"
                    fourier_mask.zoom_amnt = zoom_f
                    fourier_mask.width = sample.width
                    fourier_mask.height = sample.height
                }
                else{
                    deactivate_mask_mode()
                    highlighted = false
                    button_apply.enabled = false
                    button_load.enabled = false
                    button_save.enabled = false
                    bg.state = "normal"
                }
            }
            /* function to be used for outside calls to turn off masking mode */
            function deactivate(){
                deactivate_mask_mode()
                highlighted = false
                button_apply.enabled = false
                button_load.enabled = false
                button_save.enabled = false
                bg.state = "normal"
            }
        }

        Slider {
            signal qml_signal_send_perf_mode(int perf_val)
            id: slider_performance
            objectName: "slider_performance"
            x: 503
            y: 708
            width: 82
            height: 34
            snapMode: Slider.SnapAlways
            stepSize: 4
            from: 8
            value: 1
            onValueChanged: {
                qml_signal_send_perf_mode(value)
            }
            Component.onCompleted: {
                qml_signal_send_perf_mode(value)
            }
        }

        Label {
            id: label_hp
            x: 382
            y: 718
            height: 14
            text: qsTr("High Performance")
        }

        Label {
            id: label_hq
            x: 584
            y: 716
            text: qsTr("High Quality")
        }
    }


    Button {
        signal qml_signal_stop_streaming
        signal qml_signal_close
        id: button_close
        objectName: "button_close"
        x: 569
        y: 822
        text: qsTr("Close")

        onClicked: {
            dhmx_holo_disp.visible = false
            qml_signal_stop_streaming()
            qml_signal_close()
            button_mask.deactivate()
        }
    }

    Label {
        id: label
        x: 33
        y: 20
        text: combo_disp.textAt(combo_disp.currentIndex)+" Display"
        font.pointSize: 18
    }

    Rectangle {
        id: sample_area
        objectName: "sample_area"
        x: 33
        y: 70
        width: frame_width
        height: frame_height
        visible: true
        enabled: true
        clip: true
        color: "#00ffffff"

        Flickable{
            id: flickArea
            objectName: "canvas_area"
            width: parent.width
            height: parent.height
            contentWidth: sample.width*sample.scale
            contentHeight: sample.height*sample.scale


            MouseArea{
                id: zoom_area
                height: flickArea.height
                width: flickArea.width
                anchors.fill:parent

                onWheel: {
                    zoom(wheel.angleDelta.y)
                    update_zoom(sample)
                    //update_zoom(fourier_mask_sample)
                }
                onMouseXChanged: {
                    flickArea.anchors.horizontalCenterOffset = zoom_area.mouseX

                }
                onMouseYChanged: {
                    flickArea.anchors.verticalCenterOffset = zoom_area.mouseY

                }

                MouseArea{
                    id: pixel_value
                    signal qml_signal_mouse_pos(int x,int y)
                    objectName: "pixel_value"
                    width: sample.width
                    height: sample.height
                    hoverEnabled: true

                    onMouseXChanged: {
                        var positionInRoot = mapToItem(sample, mouse.x, mouse.y)
                        qml_signal_mouse_pos(positionInRoot.x, positionInRoot.y)
                    }
                }

                Image {
                    property bool counter: false
                    id: sample
                    objectName: "image_sample"
                    asynchronous: false
                    cache: false
                    smooth: false

                    function reload(){
                        counter = !counter
                        source = "image://"+combo_disp.textAt(combo_disp.currentIndex)+"/image?id="+counter
                    }

                    Component.onCompleted: {
                        source = ""
                    }
                }
                Image {
                    id: fourier_mask_sample
                    cache: false
                    visible: false
                    enabled: true
                    smooth: false
                    width: frame_width
                    height: frame_height

                    onVisibleChanged: {
                        fourier_mask_sample.width = sample.width
                        fourier_mask_sample.height = sample.height
                        update_zoom(fourier_mask_sample)
                        fourier_mask.zoom_amnt = get_zoom_amnt(fourier_mask_sample)
                    }
                    /* The drawing canvas for fourier mode */
                    DhmxMaskingMode{
                        id: fourier_mask
                        objectName: "fourier_mask"
                        anchors.fill:parent
                        //width: 636
                        //height: 636
                        visible: false
                        enabled: false
                        max_wavelength: max_wavelength

                        onVisibleChanged: {
                            fourier_mask_sample.width = sample.width
                            fourier_mask_sample.height = sample.height
                            update_zoom(fourier_mask_sample)
                            fourier_mask.update_all_positions(zoom_f)
                        }
                    }
                }

            }
        }
    }

    Label {
        id: label_zoom
        x: 125
        y: 713
        width: 44
        height: 17
        text: qsTr("Scale:")
        font.bold: true
    }



    Label {
        id: label_zoom_amnt
        objectName: "label_zoom_amnt"
        x: 177
        y: 713
        text: "100.00%"
    }

    DhmxHistogram{
        z:100
        id: subwin_histogram
        x: 33
        y: 70
        objectName: "subwin_histogram"
        width: 636
        height: 150
        opacity: 0.0
        enabled: false

        states: [
            State { name: "visible";
                PropertyChanges { target: subwin_histogram; opacity: 0.9}
            },
            State { name: "invisible";
                PropertyChanges { target: subwin_histogram; opacity: 0.0}
            }
        ]
        transitions: Transition{
            NumberAnimation {property: "opacity"; duration: 500}
        }

    }

    Label {
        id: label_timestamp
        x: 88
        y: 733
        text: qsTr("Timestamp:")
        font.bold: true
    }

    Label {
        id: label_time
        x: 178
        y: 734
        text: "00:00:00"
        font.pointSize: 10
        objectName: "label_time"
    }


    Item {
        id: reconst
        states: [
            State { name: "visible";
                PropertyChanges { target: reconst; opacity: 1.0}
            },
            State { name: "invisible";
                PropertyChanges { target: reconst; opacity: 0.0}
            }
        ]
        transitions: Transition{
            NumberAnimation {property: "opacity"; duration: 500}
        }
        Label {
            id: label_prop_dist
            x: 350
            y: 750
            text: "Propagation Distance Index"
            font.bold: true
        }
        SpinBox {
            signal qml_signal_set_prop_dist(int distance)
            id: spinBox_prop_dist
            objectName: "spinBox_prop_dist"
            x: 557
            y: 746
            width: 112
            height: 25
            from: 1
            onValueChanged: {
                qml_signal_set_prop_dist(spinBox_prop_dist.value)
            }
        }
        Label {
            id: label_wavelength
            x: 418
            y: 783
            text: "Wavelength Index"
            font.bold: true
        }
        SpinBox {
            signal qml_signal_set_wavelegnth(int value)
            id: spinBox_wavelength
            objectName: "spinBox_wavelength"
            x: 557
            y: 779
            from: 1
            width: 112
            height: 25

            onValueChanged: {
                qml_signal_set_wavelegnth(spinBox_wavelength.value)
            }
        }
    }

    Button {
        signal qml_signal_fourier_mask_cmd()
        id: button_apply
        objectName: "button_apply"
        x: 33
        y: 822
        text: qsTr("Apply Mask")
        enabled: false
        onClicked: {
            qml_signal_fourier_mask_cmd()
        }
    }

    Button {
        id: button_save
        x: 139
        y: 822
        text: qsTr("Save Mask")
        enabled: false
    }

    Button {
        id: button_load
        x: 245
        y: 822
        text: qsTr("Load Mask")
        enabled: false
    }

    Label {
        id: label_framesource
        x: 76
        y: 754
        text: qsTr("Framesource:")
        font.bold: true
    }

    Label {
        id: label_source
        objectName: "label_source"
        x: 178
        y: 754
        text: "None"
    }

    Label {
        id: label_generating_frames
        x: 39
        y: 796
        text: qsTr("Generating Frames:")
        font.bold: true
    }

    Image {
        id: icon_playback_status
        objectName: "icon_playback_status"
        x: 179
        y: 798
        width: 15
        height: 15
        source: "images/icon_status_bad.png"

        function setPlaying(){
            source = "images/icon_status_good.png"
        }
        function setStopped(){
            source = "images/icon_status_bad.png"
        }
    }

    Label {
        id: label_pixelval
        x: 88
        y: 775
        text: qsTr("Pixel Value:")
        font.bold: true
    }

    Label {
        id: label_pixelval_amnt
        objectName: "label_pixelval_amnt"
        x: 178
        y: 775
        text: "0"
    }
    function reset_view(){
        sample.width = start_width
        sample.height = start_height
        set_aspect_ratio()
    }

    function update_timetag(timetag){
        /* the UTC time for HH:MM:SS including cleanup */
        label_time.text = timetag
    }

    function set_histogram_val(iterator,value){
        subwin_histogram.set_val(iterator,value)
    }

    function update_zoom(id){
        var curr_zoom
        var ammount
        curr_zoom = id.width / source_width
        curr_zoom = curr_zoom * 100
        ammount = curr_zoom.toFixed(2)+"%"
        label_zoom_amnt.text = ammount
        get_zoom_amnt(id)
    }

    function get_zoom_amnt(id){
        var zoom
        zoom = id.width  / source_width
        dhmx_holo_disp.zoom_f = zoom
        set_aspect_ratio()
        fourier_mask.set_initial_zoom(zoom)
        return zoom
    }

    function set_aspect_ratio(){
        aspect_ratio = start_width / start_height
    }

    function update_image(image_url){
        sample.source = image_url
    }

    function zoom(zoom){     
        if(!(start_height > sample.height+zoom)){
            sample.width += zoom
            sample.height += zoom/aspect_ratio
        }
        else{
            sample.width = start_width
            sample.height = start_height
        }

    }
    function get_zoom(){
        return sample_width
    }

    function set_display(type){
        combo_disp.currentIndex = combo_disp.find(type)
    }

    function activate_mask_mode(){
        console.log("Enabling masking mode")
        fourier_mask.max_wavelength = max_wavelength
        fourier_mask.zoom_amnt = get_zoom_amnt(fourier_mask_sample)
        fourier_mask.enabled = true
        fourier_mask.visible = true
        fourier_mask_sample.source = sample.source
        fourier_mask_sample.visible = true
        fourier_mask_sample.update()

    }
    function deactivate_mask_mode(){
        console.log("Disabling masking mode")
        fourier_mask.enabled = false
        fourier_mask.visible = false
        fourier_mask_sample.source = sample.source
        fourier_mask_sample.visible = false
        fourier_mask_sample.update()
    }
    function add_circle(name,x,y,radius){
        //set first command
        if(fourier_mask_cmd == ""){
            fourier_mask_cmd = "fouriermask mask_"+name+"=["+x+","+y+","+radius+"]"
        }
        //n-additional circles added this way
        else{
            fourier_mask_cmd += ",mask_"+name+"=["+x+","+y+","+radius+"]"
        }
    }
    function pack_cmd(){
        if(fourier_mask.wavelength1 != undefined){
            add_circle("circle_1",fourier_mask.wavelength1.position_x,fourier_mask.wavelength1.position_y,fourier_mask.wavelength1.r_actual)
        }
        if(fourier_mask.wavelength2 != undefined){
            add_circle("circle_2",fourier_mask.wavelength2.position_x,fourier_mask.wavelength2.position_y,fourier_mask.wavelength2.r_actual)
        }
        if(fourier_mask.wavelength3 != undefined){
            add_circle("circle_3",fourier_mask.wavelength3.position_x,fourier_mask.wavelength3.position_y,fourier_mask.wavelength3.r_actual)
        }
        fourier_mask_cmd = ""

    }
    function update_wl(wl){
        max_wavelength = wl
        fourier_mask.max_wavelength = wl
    }

    function set_source_width_and_height(width, height){
        source_height = width
        source_width = height
    }

    function set_histogram_pixel_count(pixel_count){
        subwin_histogram.bin_amnt = pixel_count
    }
}
