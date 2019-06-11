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

        Frame {
            id: item_input_region
            x: 0
            y: 525
            width: 300
            height: 243
            anchors.right: parent.right
            anchors.rightMargin: 0

            Rectangle {
                id: rectangle_bg
                x: 21
                y: 265
                color: "#a7a1a1"
                anchors.leftMargin: -12
                anchors.rightMargin: -12
                anchors.bottomMargin: -12
                anchors.topMargin: -12
                border.width: 0
                anchors.fill: parent
            }

            SpinBox {
                id: spinBox_ir_col
                x: 161
                y: 96
                width: 115
                height: 30
                enabled: false
            }

            Label {
                id: label_ir_col
                x: 96
                y: 103
                text: qsTr("Column")
            }

            SpinBox {
                id: spinBox_ir_row
                x: 161
                y: 21
                width: 115
                height: 30
                enabled: false
            }

            Label {
                id: label_ir_row
                x: 115
                y: 28
                text: qsTr("Row")
            }

            SpinBox {
                id: spinBox_ir_height
                x: 161
                y: 134
                width: 115
                height: 30
                enabled: false
            }

            Label {
                id: label_ir_height
                x: 101
                y: 141
                text: qsTr("Height")
            }

            SpinBox {
                id: spinBox_ir_width
                x: 161
                y: 59
                width: 115
                height: 30
                enabled: false
            }

            Label {
                id: label_ir_width
                x: 107
                y: 66
                text: qsTr("Width")
            }

            Label {
                id: label_input_region
                x: 62
                y: 5
                text: qsTr("Input Region")
                font.bold: true
            }

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

                SpinBox {
                    id: spinBox_gain
                    x: 182
                    y: 32
                    width: 109
                    height: 32
                    leftPadding: 46
                    topPadding: 6
                    enabled: false
                    anchors.right: parent.right
                    anchors.rightMargin: 10
                }

                Slider {
                    id: slider_gain
                    y: 28
                    height: 40
                    enabled: false
                    to: 255
                    from: 0
                    anchors.right: parent.right
                    anchors.rightMargin: 127
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    value: 0
                }

                Label {
                    id: label_gain
                    y: 15
                    width: 30
                    height: 17
                    text: qsTr("Gain")
                    font.bold: true
                    anchors.left: parent.left
                    anchors.leftMargin: 13
                }
            }

            Item {
                id: item_brightness
                x: 0
                y: 57
                width: 301
                height: 68
                SpinBox {
                    id: spinBox_brightness
                    x: 182
                    y: 32
                    width: 109
                    height: 32
                    topPadding: 6
                    anchors.right: parent.right
                    leftPadding: 46
                    anchors.rightMargin: 10
                    enabled: false
                }

                Slider {
                    id: slider_brightness
                    y: 28
                    height: 40
                    anchors.right: parent.right
                    value: 0
                    anchors.leftMargin: 8
                    to: 255
                    from: 0
                    anchors.left: parent.left
                    anchors.rightMargin: 127
                    enabled: false
                }

                Label {
                    id: label_brightness
                    y: 15
                    width: 69
                    height: 17
                    text: qsTr("Brightness")
                    anchors.leftMargin: 13
                    font.bold: true
                    anchors.left: parent.left
                }
            }

            Item {
                id: item_shutter
                x: 0
                y: 113
                width: 301
                height: 68
                SpinBox {
                    id: spinBox_shutter
                    x: 182
                    y: 32
                    width: 109
                    height: 32
                    topPadding: 6
                    anchors.right: parent.right
                    leftPadding: 46
                    anchors.rightMargin: 10
                    enabled: false
                }

                Slider {
                    id: slider_shutter
                    y: 28
                    height: 40
                    anchors.right: parent.right
                    value: 0
                    anchors.leftMargin: 8
                    to: 255
                    from: 0
                    anchors.left: parent.left
                    anchors.rightMargin: 127
                    enabled: false
                }

                Label {
                    id: label_shutter
                    y: 15
                    width: 81
                    height: 17
                    text: qsTr("Shutter (ms)")
                    anchors.leftMargin: 13
                    font.bold: true
                    anchors.left: parent.left
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
                anchors.leftMargin: 73
            }
        }

        CheckDelegate {
            id: checkDelegate_recording
            objectName: "check_recording"
            x: 140
            y: 372
            text: qsTr("Enable Recording")
            anchors.right: parent.right
            anchors.rightMargin: -2
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
            x: 56
            y: 38
            width: 55
            height: 30
            text: qsTr("Load")
            anchors.right: parent.right
            anchors.rightMargin: 177
            enabled: false
        }

        Button {
            id: button_close
            x: 610
            y: 38
            width: 55
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
            x: 14
            y: 38
            width: 55
            height: 30
            text: qsTr("Save")
            anchors.right: parent.right
            anchors.rightMargin: 238
            enabled: false
        }

        Button {
            id: button_apply
            x: 117
            objectName: "button_apply"
            y: 38
            width: 55
            height: 30
            text: qsTr("Apply")
            anchors.right: parent.right
            anchors.rightMargin: 116
        }



    }



}



































































/*##^## Designer {
    D{i:1;invisible:true}D{i:3;anchors_height:650;anchors_width:650;anchors_x:33;anchors_y:76}
D{i:6;anchors_height:200;anchors_width:200}D{i:19;anchors_x:52}D{i:18;anchors_width:380;anchors_x:52}
D{i:23;anchors_x:52}D{i:22;anchors_width:380;anchors_x:52}D{i:27;anchors_x:52}D{i:26;anchors_width:380;anchors_x:52}
D{i:32;anchors_x:129}D{i:5;anchors_height:90;anchors_y:242}D{i:35;anchors_width:50;anchors_x:134}
D{i:37;anchors_width:50;anchors_x:14}D{i:38;anchors_width:50;anchors_x:255}D{i:34;anchors_width:718;anchors_x:0}
}
 ##^##*/
