import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3


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
            x: 348
            y: 15
            width: 155
            height: 51
            source: "images/dhmx_blk.png"
            fillMode: Image.PreserveAspectFit
        }
    }


    Image {
        property bool counter: false
        y: 76
        id: sample
        width: 650
        height: 650
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 124
        anchors.left: parent.left
        anchors.leftMargin: 33
        objectName: "image_sample"
        asynchronous: false
        cache: false

        function reload(){
            counter = !counter
            source = "image://Hologram/image?id="+counter
        }

        Component.onCompleted: {
            source = ""
            // sample.width = sample_area.width
            // sample.height = sample_area.height
            // update_zoom(sample)

        }
    }



    Label {
        id: label_camera_settings
        x: 316
        y: 48
        text: qsTr("Camera Settings")
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
            y: 321
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
                anchors.leftMargin: 68
            }
        }

        CheckDelegate {
            id: checkDelegate_recording
            objectName: "check_recording"
            signal qml_signal_recording(bool checked)
            x: 140
            y: 372
            text: qsTr("Enable Recording")
            anchors.right: parent.right
            anchors.rightMargin: -2

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
            x: 66
            y: 38
            width: 60
            height: 30
            text: qsTr("Load")
            anchors.right: parent.right
            anchors.rightMargin: 162
            enabled: false
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
            x: 0
            y: 38
            width: 60
            height: 30
            text: qsTr("Save")
            anchors.right: parent.right
            anchors.rightMargin: 228
            enabled: false
        }
    }

    Label {
        id: label_width
        x: 45
        y: 768
        text: qsTr("Image Width:")
        font.pointSize: 11
        font.bold: true
    }

    Label {
        id: label_height
        x: 39
        y: 796
        text: qsTr("Image Height:")
        font.bold: true
        font.pointSize: 11
    }

    Label {
        id: label_frame_id
        x: 310
        y: 796
        text: qsTr("Frame ID:")
        font.bold: true
        font.pointSize: 11
    }

    Label {
        id: label_timestamp
        x: 294
        y: 768
        text: qsTr("Timestamp:")
        font.bold: true
        font.pointSize: 11
    }

    Label {
        id: label_frame_id_data
        x: 388
        objectName: "label_frame_id_data"
        y: 796
        text: qsTr("000")
        font.bold: false
        font.pointSize: 11
    }

    Label {
        id: label_timestamp_data
        x: 388
        objectName: "label_timestamp_data"
        y: 768
        text: qsTr("00:00:00")
        font.bold: false
        font.pointSize: 11
    }

    Label {
        id: label_width_data
        x: 152
        objectName: "label_width_data"
        y: 768
        text: qsTr("0")
        font.bold: false
        font.pointSize: 11
    }

    Label {
        id: label_height_data
        x: 152
        objectName: "label_height_data"
        y: 796
        text: qsTr("0")
        font.bold: false
        font.pointSize: 11
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



}

































































































/*##^## Designer {
    D{i:1;invisible:true}D{i:3;anchors_height:650;anchors_width:650;anchors_x:33;anchors_y:76}
D{i:7;anchors_width:380;anchors_x:52}D{i:11;anchors_width:380;anchors_x:52}D{i:16;anchors_x:129}
D{i:17;anchors_x:129}D{i:18;anchors_width:718;anchors_x:0}D{i:5;anchors_height:90;anchors_y:242}
D{i:20;anchors_width:50;anchors_x:134}D{i:21;anchors_width:50;anchors_x:14}D{i:22;anchors_width:50;anchors_x:255}
D{i:23;anchors_width:50;anchors_x:45}D{i:19;anchors_width:50;anchors_x:134}D{i:24;anchors_x:39}
D{i:25;anchors_x:310}D{i:26;anchors_x:294}D{i:27;anchors_x:388}D{i:28;anchors_x:388}
D{i:29;anchors_x:152}D{i:30;anchors_x:152}D{i:31;anchors_x:152}
}
 ##^##*/
