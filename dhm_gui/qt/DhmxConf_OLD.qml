import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3


Rectangle {
    id: dhmx_config
    visible: true
    width: 750
    height: 830
    color: "#c1bebe"
    border.color: "#242424"
    border.width: 4
    //   title: qsTr("Configuration Parameters")

    Drag.active: drag_area.drag.active
    Drag.hotSpot.x: 10
    Drag.hotSpot.y: 10

    MouseArea {
        id: drag_area
        height: 900
        anchors.fill: parent
        drag.target: parent
    }


    Button {
        id: button_save
        x: 139
        y: 767
        text: qsTr("Save")
    }

    Button {
        id: button_cancel
        x: 461
        y: 767
        text: qsTr("Cancel")

        onClicked: {
            dhmx_config.visible = false
        }
    }

    Label {
        id: label_filename
        x: 51
        y: 93
        text: qsTr("File Name")
    }

    TextField {
        id: textField_fn
        x: 139
        y: 81
        width: 422
        height: 40
        text: qsTr("/home/DHM/file")
    }

    Button {
        id: button_load
        x: 585
        y: 81
        text: qsTr("Load From File")

        onClicked: {
            var component = Qt.createComponent("DhmxFD.qml");
            var window = component.createObject(this);
        }
    }

    Label {
        id: label_desc
        x: 39
        y: 135
        width: 80
        height: 16
        text: qsTr("Description")

    }

    Label {
        id: label_width
        x: 78
        y: 361
        width: 41
        height: 17
        text: qsTr("Width")
    }

    SpinBox {
        id: spinBox_width
        x: 141
        y: 349
    }

    Label {
        id: label_height
        x: 73
        y: 417
        text: qsTr("Height")
    }

    SpinBox {
        id: spinBox_height
        x: 141
        y: 405
    }

    TextArea {
        background: Rectangle{
            anchors.fill: parent
            color:"white"
        }

        id: textArea_desc
        x: 141
        y: 135
        width: 420
        height: 81
        text: qsTr("Description of file")
    }

    Label {
        id: label_pixel_x
        x: 301
        y: 361
        width: 86
        height: 17
        text: qsTr("Pixel Pitch x")
    }

    SpinBox {
        id: spinBox_pixel_x
        x: 390
        y: 349
        stepSize: 0
    }

    Label {
        id: label_pixel_y
        x: 301
        y: 417
        width: 86
        height: 17
        text: qsTr("Pixel Pitch y")
    }

    SpinBox {
        id: spinBox_pixel_y
        x: 390
        y: 405
        width: 140
        height: 40
        stepSize: 0
    }

    TabBar{
        id: bar
        x: 141
        y: 492
        width: 420
        height: 214
        currentIndex: 0

        TabButton{
            //    x: 0
            //    y: -39
            text: qsTr("Light Source Parameters")
        }
        TabButton{
            //    x: 206
            //    y: -39
            text: qsTr("Hologram Parameters")
        }
    }

    StackLayout{
        x: 0
        y: -53
        currentIndex: bar.currentIndex

        Item{
            id: tab1

            Label {
                id: label_nm_1
                x: 508
                y: 714
                text: qsTr("nm")
            }

            Label {
                id: label_nm_2
                x: 508
                y: 664
                text: qsTr("nm")
            }

            Label {
                id: label_nm_3
                x: 508
                y: 614
                text: qsTr("nm")
            }

            SpinBox {
                id: spinBox_wl_1
                x: 359
                y: 605
                stepSize: 0
            }

            SpinBox {
                id: spinBox_wl_2
                x: 359
                y: 654
                stepSize: 0
            }

            SpinBox {
                id: spinBox_wl_3
                x: 359
                y: 703
                stepSize: 0
            }

            SpinBox {
                id: spinbox_wl_main
                x: 168
                y: 654
                to: 3
                from: 1
                value: 1

                onValueChanged: {
                    update_wl()
                }

            }

            Label {
                id: label_wl
                x: 192
                y: 631
                text: qsTr("Number of wl")
            }
        }

        Item{
            id: tab2

            SpinBox {
                id: spinBox_rebin_factor
                x: 348
                y: 676
            }

            SpinBox {
                id: spinBox_crop_fraction
                x: 348
                y: 619
            }

            Label {
                id: label_rebin
                x: 219
                y: 630
                text: qsTr("Rebin Factor")
            }

            Label {
                id: label_crop
                x: 212
                y: 687
                text: qsTr("Crop Fraction")
            }
        }

    }

    Label {
        id: label
        x: 16
        y: 20
        text: qsTr("Session Parameters")
        font.bold: false
        font.pointSize: 18
    }

    Label {
        id: label_info
        x: 45
        y: 227
        width: 74
        height: 16
        text: qsTr("Lense Info")
    }

    TextArea {
        id: textArea_info
        x: 141
        y: 227
        width: 420
        height: 78
        text: qsTr("Lense related information")
        background: Rectangle {
            color: "#ffffff"
            anchors.fill: parent
        }
    }

    Label {
        id: label_um
        x: 536
        y: 361
        width: 26
        height: 17
        text: qsTr("µm")
    }

    Label {
        id: label_um1
        x: 536
        y: 417
        width: 26
        height: 17
        text: qsTr("µm")
    }



    /* Update fields as soon as the window is opened */
    onVisibleChanged: {
        //  onActiveChanged: {
        update_wl()
    }

    /* Functions to change visibility and sensitivity of fields */
    function update_wl(){
        if(spinbox_wl_main.value == "1"){
            spinBox_wl_1.enabled = true
            spinBox_wl_2.enabled = false
            spinBox_wl_3.enabled = false
        }
        if(spinbox_wl_main.value == "2"){
            spinBox_wl_1.enabled = true
            spinBox_wl_2.enabled = true
            spinBox_wl_3.enabled = false
        }
        if(spinbox_wl_main.value == "3"){
            spinBox_wl_1.enabled = true
            spinBox_wl_2.enabled = true
            spinBox_wl_3.enabled = true
        }
    }
}

