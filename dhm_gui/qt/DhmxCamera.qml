import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3


ApplicationWindow {
    id: dhmx_camera
    visible: true
    width: 850
    height: 500

    title: "DHMx Camera Settings v0.8.0   06-04-2019"

    Rectangle {
        id: bg
        width: 800
        anchors.fill: parent

        color: "#c1bebe"
        border.color: "#242424"
        border.width: 2

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


    /* Scaling handle */
    Button {
        id: button_apply
        objectName: "button_apply"
        x: 273
        y: 435
        text: qsTr("Apply")
    }

    Button {
        id: button_close
        x: 709
        y: 435
        text: qsTr("Close")

        onClicked: {
            Qt.quit()
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

    Item {
        id: item_fps
        x: 558
        y: 241
        width: 272
        height: 74

        SpinBox {
            id: spinBox_fps
            x: 116
            y: 18
            enabled: false
        }

        Label {
            id: label_fps
            x: 9
            y: 30
            text: qsTr("Framerate (fps)")
        }
    }

    Frame {
        id: item_input_region
        x: 32
        y: 250
        width: 470
        height: 164

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
            x: 281
            y: 18
            enabled: false
        }

        Label {
            id: label_ir_col
            x: 223
            y: 30
            text: qsTr("Column")
        }

        SpinBox {
            id: spinBox_ir_row
            x: 51
            y: 18
            enabled: false
        }

        Label {
            id: label_ir_row
            x: 15
            y: 30
            text: qsTr("Row")
        }

        SpinBox {
            id: spinBox_ir_height
            x: 281
            y: 81
            enabled: false
        }

        Label {
            id: label_ir_height
            x: 229
            y: 93
            text: qsTr("Height")
        }

        SpinBox {
            id: spinBox_ir_width
            x: 51
            y: 81
            enabled: false
        }

        Label {
            id: label_ir_width
            x: 4
            y: 93
            text: qsTr("Width")
        }

        Label {
            id: label_input_region
            x: -6
            y: -6
            text: qsTr("Input Region")
            font.bold: true
        }

    }

    Item {
        id: item_camera_controls
        x: 22
        y: 83
        width: 807
        height: 156
        visible: true

        Item {
            id: item_shutter
            x: -1
            y: 107
            width: 796
            height: 41

            DoubleSpinBox {
                id: spinBox_shutter
                x: 656
                y: 0
                width: 140
                height: 40
                enabled: false
                decimals: 3
                realEdit: true
                realTo: 255.000
                realFrom: 0.000
                realValue: 0.000
                realStepSize: 0.01

                anchors.right: parent.right
                anchors.rightMargin: 0

                onValueChanged: {
                    slider_shutter.value = (spinBox_shutter.value / spinBox_shutter.factor)
                }
            }

            Slider {
                id: slider_shutter
                y: 0
                height: 40
                enabled: false
                to: 255
                from: 0
                anchors.right: parent.right
                anchors.rightMargin: 161
                anchors.left: parent.left
                anchors.leftMargin: 92
                value: 0

                onPressedChanged: {
                    spinBox_shutter.realValue = slider_shutter.value
                    /* Send command only on release */
                    if(!pressed){
                        //future todo
                    }
                }

            }

            Label {
                id: label_shutter
                y: 12
                width: 86
                height: 17
                text: qsTr("Shutter (ms)")
                anchors.left: parent.left
                anchors.leftMargin: 9
            }
        }

        Item {
            id: item_brightness
            x: -1
            y: 60
            width: 796
            height: 41
            SpinBox {
                id: spinBox_brightness
                x: 493
                y: 0
                enabled: false
                anchors.right: parent.right
                anchors.rightMargin: 0
            }

            Slider {
                id: slider_brightness
                y: 0
                height: 40
                enabled: false
                to: 255
                from: 0
                anchors.right: parent.right
                anchors.rightMargin: 161
                anchors.left: parent.left
                anchors.leftMargin: 92
                value: 0

            }

            Label {
                id: label_brightness
                y: 12
                width: 72
                height: 17
                text: qsTr("Brightness")
                anchors.left: parent.left
                anchors.leftMargin: 18
            }
        }

        Item {
            id: item_gain
            x: -1
            y: 13
            width: 796
            height: 41

            SpinBox {
                id: spinBox_gain
                x: 493
                y: 0
                enabled: false
                anchors.right: parent.right
                anchors.rightMargin: 0
            }

            Slider {
                id: slider_gain
                y: 0
                height: 40
                enabled: false
                to: 255
                from: 0
                anchors.right: parent.right
                anchors.rightMargin: 161
                anchors.left: parent.left
                anchors.leftMargin: 92
                value: 0
            }

            Label {
                id: label_gain
                y: 12
                width: 30
                height: 17
                text: qsTr("Gain")
                anchors.left: parent.left
                anchors.leftMargin: 55
            }
        }
    }

    CheckDelegate {
        id: checkDelegate_recording
        objectName: "check_recording"
        x: 550
        y: 306
        text: qsTr("Enable Recording")
    }

    Button {
        id: button_save
        x: 32
        y: 435
        text: qsTr("Save")
        enabled: false
    }

    Button {
        id: button_load
        x: 152
        y: 435
        text: qsTr("Load")
        enabled: false
    }



}



































/*##^## Designer {
    D{i:1;invisible:true}D{i:10;anchors_height:200;anchors_width:200}D{i:22;anchors_x:0}
D{i:23;anchors_x:0}D{i:26;anchors_width:380;anchors_x:10}D{i:27;anchors_x:94}D{i:28;anchors_x:94}
D{i:25;anchors_width:380;anchors_x:92}D{i:30;anchors_width:380;anchors_x:52}D{i:31;anchors_x:52}
D{i:29;anchors_width:380;anchors_x:92}
}
 ##^##*/
