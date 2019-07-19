import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3
import QtGraphicalEffects 1.0

ApplicationWindow {
    id: dhmx_camera
    visible: true
    width: 1024
    height: 850

    minimumWidth: 800
    minimumHeight: 765

    signal send_cmd(string cmd)
    property int gain_min: 0
    property int gain_max: 1
    property int exposure_min: 0
    property int exposure_max: 1
    property int framerate: 0

    /* This function below will help keep the view centered at all times
     * during a resize or maximize event
     */
    onWidthChanged: {
        reset_view()
    }

    Rectangle {
        id: bg
        width: 800
        height: 500
        anchors.fill: parent

        color: "#c1bebe"
        border.color: "#242424"
        border.width: 0

        Image {
            id: image
            y: 15
            height: 51
            anchors.left: parent.left
            anchors.leftMargin: 348
            anchors.right: parent.right
            anchors.rightMargin: 521
            source: "images/dhmx_blk.png"
            fillMode: Image.PreserveAspectFit
        }

        Rectangle {
            id: bottom_panel
            x: 27
            y: 753
            width: 648
            height: 73
            color: "#a7a1a1"
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 24
            layer.enabled: enabled

            /* Dropshadow effect */
            layer.effect: DropShadow {
                anchors.fill: bottom_panel
                horizontalOffset: -10
                verticalOffset: 5
                radius: 5
                samples: 5
                color: "#999"
                source: bottom_panel
            }
        }
    }


    Rectangle {
        id: sample_area
        visible: true
        enabled: true
        clip: true
        color: "#00ffffff"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 125
        anchors.right: parent.right
        anchors.rightMargin: 341
        anchors.top: parent.top
        anchors.topMargin: 70
        anchors.left: parent.left
        anchors.leftMargin: 33

        Flickable{
            id: flickArea
            width: parent.width
            height: parent.height
            contentWidth: sample.width*sample.scale
            contentHeight: sample.height*sample.scale
            property int start_width: parent.width
            property int start_height: parent.height
            anchors.fill: parent

            MouseArea{
                id: zoom_area
                height: flickArea.height
                width: flickArea.width
                anchors.fill:parent

                onWheel: {
                    zoom(wheel.angleDelta.y)
                }
                onMouseXChanged: {
                    flickArea.anchors.horizontalCenterOffset = zoom_area.mouseX

                }
                onMouseYChanged: {
                    flickArea.anchors.verticalCenterOffset = zoom_area.mouseY

                }

                Image {
                    property bool counter: false
                    width: sample_area.width
                    height: sample_area.height
                    fillMode: Image.PreserveAspectFit
                    id: sample
                    objectName: "image_sample"
                    asynchronous: false
                    cache: false
                    smooth: false


                    function reload(){
                        counter = !counter
                        source = "image://Hologram/image?id="+counter
                    }

                    Component.onCompleted: {
                        source = ""
                        //sample.width = sample_area.width
                        //sample.height = sample_area.height
                        update_zoom(sample)

                    }
                }
            }
        }

    }
    Label {
        id: label_camera_settings
        x: 316
        y: 47
        width: 121
        height: 17
        text: qsTr("Camera Settings")
        anchors.horizontalCenterOffset: -132
        anchors.horizontalCenter: parent.horizontalCenter
        font.bold: true
        font.pointSize: 11
    }


    Rectangle {
        id: side_panel
        x: 724
        width: 300
        color: "#a7a1a1"
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
        border.width: 0
        layer.enabled: enabled


        /* Dropshadow effect */
        layer.effect: DropShadow {
            anchors.fill: side_panel
            horizontalOffset: -10
            radius: 5
            samples: 5
            color: "#999"
            source: side_panel
        }

        Item {
            id: item_camera_controls
            x: 0
            y: 49
            width: 300
            height: 236
            anchors.right: parent.right
            anchors.rightMargin: 0
            visible: true

            Item {
                id: item_gain
                x: 0
                y: 0
                width: 301
                height: 68

                Slider {
                    id: slider_gain
                    objectName: "slider_gain"
                    y: 28
                    height: 40
                    enabled: true
                    to: gain_max
                    from: gain_min
                    anchors.right: parent.right
                    anchors.rightMargin: 99
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    value: 0
                    onValueChanged: {
                        textField_gain.text = parseInt(slider_gain.value)

                    }
                    onPressedChanged: {
                        if(!pressed){
                            send_cmd("GAIN="+parseInt(slider_gain.value))
                        }
                    }
                }

                Label {
                    id: label_gain
                    y: 15
                    width: 30
                    height: 17
                    text: qsTr("Gain (dB)")
                    font.bold: true
                    anchors.left: parent.left
                    anchors.leftMargin: 13
                }

                TextField {
                    id: textField_gain
                    objectName: "textField_gain"
                    x: 208
                    y: 28
                    width: 83
                    height: 36
                    inputMethodHints: Qt.ImhPreferNumbers
                    text: qsTr("0")
                    placeholderText: ""
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                    maximumLength: 2
                    selectByMouse: true

                    Keys.onReturnPressed: {
                        if(textField_gain.text > gain_max){
                            textField_gain.text = gain_max
                        }
                        if(textField_gain.text < gain_min){
                            textField_gain.text = gain_min
                        }
                        slider_gain.value = textField_gain.text
                        send_cmd("GAIN="+textField_gain.text)
                    }
                }
            }

            Item {
                id: item_shutter
                x: 0
                y: 57
                width: 301
                height: 68

                Slider {
                    id: slider_exposure
                    objectName: "slider_exposure"
                    y: 28
                    height: 40
                    anchors.right: parent.right
                    value: 0
                    anchors.leftMargin: 8
                    //to: exposure_max
                    //from: exposure_min
                    to: 100
                    from: 0
                    anchors.left: parent.left
                    anchors.rightMargin: 99
                    enabled: true
                    onValueChanged: {
                        // textField_exposure.text = parseInt(slider_exposure.value)
                        if(!textField_exposure.fromText){
                            textField_exposure.text = parseInt(slider_to_log(from,to,exposure_min,exposure_max,value))
                        }
                        else{
                            slider_exposure.value = parseInt(text_to_slider(from,to,exposure_min,exposure_max, parseInt(textField_exposure.text)))
                            textField_exposure.fromText = false
                        }
                    }
                    onPressedChanged: {
                        if(!pressed){
                            send_cmd("EXPOSURE="+parseInt(slider_to_log(from,to,exposure_min,exposure_max,value)))
                        }
                    }
                }

                Label {
                    id: label_shutter
                    y: 15
                    width: 81
                    height: 17
                    text: qsTr("Exposure (us)")
                    anchors.leftMargin: 13
                    font.bold: true
                    anchors.left: parent.left
                }

                TextField {
                    id: textField_exposure
                    property bool fromText: false
                    objectName: "textField_exposure"
                    x: 221
                    y: 28
                    width: 83
                    height: 36
                    text: qsTr("0")
                    placeholderText: ""
                    anchors.rightMargin: 10
                    anchors.right: parent.right
                    inputMethodHints: Qt.ImhPreferNumbers
                    selectByMouse: true

                    Keys.onReturnPressed: {
                        if(parseInt(textField_exposure.text) > exposure_max){
                            textField_exposure.text = exposure_max
                        }
                        if(parseInt(textField_exposure.text) < exposure_min){
                            textField_exposure.text = exposure_min
                        }
                        fromText = true
                        slider_exposure.value = textField_exposure.text
                        send_cmd("EXPOSURE="+textField_exposure.text)
                    }

                }
            }
        }

        Item {
            id: item_fps
            x: 0
            y: 198
            width: 300
            height: 63
            anchors.right: parent.right
            anchors.rightMargin: 0

            SpinBox {
                id: spinBox_fps
                x: 147
                y: 10
                width: 109
                height: 32
                anchors.right: parent.right
                anchors.rightMargin: 9
                enabled: false
            }

            Label {
                id: label_fps
                y: 18
                text: qsTr("Framerate (fps)")
                font.bold: true
                anchors.left: parent.left
                anchors.leftMargin: 15
            }
        }

        CheckDelegate {
            id: checkDelegate_recording
            objectName: "check_recording"
            signal qml_signal_recording(bool checked)
            x: 117
            y: 712
            text: qsTr("Enable Recording")
            anchors.right: parent.right
            anchors.rightMargin: 0

            onCheckedChanged:{
                qml_signal_recording(checkDelegate_recording.checked)
            }
        }
    }

    Item {
        id: item_buttons
        y: 762
        height: 88
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 736

        Button {
            id: button_load
            objectName: "button_load"
            x: 66
            y: 38
            width: 60
            height: 30
            text: qsTr("Load")
            anchors.right: parent.right
            anchors.rightMargin: 162
            enabled: true
        }

        Button {
            id: button_close
            x: 217
            y: 38
            width: 63
            height: 30
            text: qsTr("Close")
            anchors.right: parent.right
            anchors.rightMargin: 8

            onClicked: {
                Qt.quit()
            }
        }

        Button {
            id: button_save
            objectName: "button_save"
            x: 0
            y: 38
            width: 60
            height: 30
            text: qsTr("Save")
            anchors.right: parent.right
            anchors.rightMargin: 228
            enabled: true
        }
    }

    Label {
        id: label_width
        x: 45
        y: 768
        text: qsTr("Image Width:")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 65
        font.pointSize: 11
        font.bold: true
    }

    Label {
        id: label_height
        x: 39
        y: 796
        text: qsTr("Image Height:")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 37
        font.bold: true
        font.pointSize: 11
    }

    Label {
        id: label_frame_id
        x: 277
        y: 796
        text: qsTr("Frame ID:")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 37
        font.bold: true
        font.pointSize: 11
    }

    Label {
        id: label_timestamp
        x: 261
        y: 768
        text: qsTr("Timestamp:")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 65
        font.bold: true
        font.pointSize: 11
    }

    Label {
        id: label_frame_id_data
        x: 351
        objectName: "label_frame_id_data"
        y: 796
        text: qsTr("000")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 37
        font.bold: false
        font.pointSize: 11
    }

    Label {
        id: label_timestamp_data
        x: 350
        objectName: "label_timestamp_data"
        y: 768
        text: qsTr("00:00:00")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 65
        font.bold: false
        font.pointSize: 11
    }

    Label {
        id: label_width_data
        x: 145
        objectName: "label_width_data"
        y: 768
        text: qsTr("0")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 65
        font.bold: false
        font.pointSize: 11
    }

    Label {
        id: label_height_data
        x: 145
        objectName: "label_height_data"
        y: 796
        text: qsTr("0")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 37
        font.bold: false
        font.pointSize: 11
    }

    Label {
        id: label_set_fps
        x: 519
        y: 768
        text: qsTr("Set FPS:")
        anchors.bottom: parent.bottom
        font.bold: true
        anchors.bottomMargin: 65
        font.pointSize: 11
    }

    Label {
        id: label_set_fps_data
        objectName: "label_set_fps_data"
        x: 583
        y: 768
        text: qsTr("000.00")
        anchors.bottom: parent.bottom
        font.bold: false
        anchors.bottomMargin: 65
        font.pointSize: 11
    }

    Label {
        id: label_current_fps
        x: 487
        y: 796
        text: qsTr("Current FPS:")
        anchors.bottom: parent.bottom
        font.bold: true
        anchors.bottomMargin: 37
        font.pointSize: 11
    }

    Label {
        id: label_current_fps_data
        objectName: "label_current_fps_data"
        x: 583
        y: 798
        text: qsTr("000.00")
        anchors.bottom: parent.bottom
        font.bold: false
        anchors.bottomMargin: 36
        font.pointSize: 11
    }

    Label {
        id: label_histogram
        x: 736
        y: 278
        width: 81
        height: 23
        text: qsTr("Histogram")
        anchors.right: parent.right
        anchors.rightMargin: 207
        font.bold: true
    }

    DhmxHistogram{
        z:100
        id: subwin_histogram
        x: 651
        y: 278
        objectName: "subwin_histogram"
        width: 405
        height: 270
        anchors.right: parent.right
        anchors.rightMargin: -32
        opacity: 1.0
        enabled: true
        visible: true
    }


    function reset_view(){
        sample.width = flickArea.start_width
        sample.height = flickArea.start_height
    }

    function zoom(zoom){
        if(!(flickArea.start_height > sample.height+zoom)){
            sample.width += zoom
            sample.height += zoom
        }
        else{
            sample.width = flickArea.start_width
            sample.height = flickArea.start_height
        }
    }

    function update_zoom(id){
        var curr_zoom
        var ammount
        curr_zoom = id.width / 2048
        curr_zoom = curr_zoom * 100
        ammount = curr_zoom.toFixed(2)+"%"
        get_zoom_amnt(id)
    }

    function get_zoom_amnt(id){
        var zoom
        zoom = id.width  / 2048
        return zoom
    }

    function slider_to_log(slider_min, slider_max, data_min, data_max, position) {
        // The slider scale
        var minp = slider_min;
        var maxp = slider_max;

        // The full scale
        var minv = Math.log(data_min);
        var maxv = Math.log(data_max);

        // calculate adjustment factor
        var scale = (maxv-minv) / (maxp-minp);
        var output = Math.exp(minv + scale*(position-minp));

        return output;
    }

    function text_to_slider(slider_min, slider_max, data_min, data_max, position){
        // The slider scale
        var minp = slider_min;
        var maxp = slider_max;

        // The full scale
        var minv = Math.log(data_min);
        var maxv = Math.log(data_max);

        // calculate adjustment factor
        var scale = (maxv-minv) / (maxp-minp);
        var output = (Math.log(position)-minv) / scale + minp;

        return output;
    }

    function apply_settings(gain,exposure){
        textField_gain.text = gain
        slider_gain.value = gain
        textField_exposure.text = exposure
        slider_exposure.value = parseInt(text_to_slider(slider_exposure.from,slider_exposure.to,exposure_min,exposure_max, parseInt(exposure)))

    }
    function set_histogram_val(iterator,value){
        subwin_histogram.set_val(iterator,value)
    }
}



















































/*##^## Designer {
    D{i:2;anchors_width:155;anchors_x:348}D{i:1;invisible:true}D{i:5;anchors_height:90;anchors_width:650;anchors_y:76}
D{i:3;anchors_height:655;anchors_width:650;anchors_x:33;anchors_y:70}D{i:7;anchors_width:121;anchors_x:316}
D{i:11;anchors_width:380;anchors_x:52}D{i:12;anchors_width:380;anchors_x:52}D{i:16;anchors_x:129}
D{i:17;anchors_x:129}D{i:19;anchors_width:50;anchors_x:134}D{i:20;anchors_width:50;anchors_x:134}
D{i:18;anchors_width:718;anchors_x:0}D{i:21;anchors_width:50;anchors_x:14}D{i:8;anchors_width:380;anchors_x:52}
D{i:23;anchors_width:50;anchors_x:45}D{i:24;anchors_width:50;anchors_x:39}D{i:25;anchors_x:310}
D{i:22;anchors_width:50;anchors_x:255}D{i:26;anchors_x:294}D{i:27;anchors_x:388}D{i:28;anchors_x:388}
D{i:29;anchors_x:152}D{i:30;anchors_x:152}D{i:31;anchors_x:152}D{i:32;anchors_x:152}
D{i:34;anchors_x:388}D{i:35;anchors_x:152}D{i:36;anchors_x:388}D{i:37;anchors_x:152}
D{i:38;anchors_width:50;anchors_x:134}
}
 ##^##*/
