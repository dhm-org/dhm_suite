import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.1

MouseArea {
    signal pack_cmd(string cmd)

    id: dhmx_port
    visible: true
    width: 400
    height: 560
    drag.target: dhmx_port
    transformOrigin: Item.TopLeft

    property variant clickX: 1
    property variant delta: 0


    Rectangle {
        id: drag_area
        anchors.fill: parent
        color: "#c1bebe"
        border.color: "#242424"
        border.width: 4
    }

    Label {
        id: label_port_list
        x: 160
        y: 57
        text: qsTr("Port List")
        font.bold: true
        font.pointSize: 14
    }

    Label {
        id: label_gui_ports
        x: 48
        y: 92
        width: 161
        height: 30
        text: qsTr("GUI Server Ports")
        font.bold: true
        font.pointSize: 14
    }

    Label {
        id: label_camera_ports
        x: 48
        y: 338
        width: 199
        height: 30
        text: qsTr("Camera Server Ports")
        font.bold: true
        font.pointSize: 14
    }

    Label {
        id: label_fourier
        x: 67
        y: 128
        text: qsTr("Fourier")
        font.pointSize: 12
    }

    Label {
        id: label_amplitude
        x: 67
        y: 159
        text: qsTr("Amplitude")
        font.pointSize: 12
    }

    Label {
        id: label_raw_frame
        x: 67
        y: 252
        text: qsTr("Raw Frame")
        font.pointSize: 12
    }

    Label {
        id: label_telemetry
        x: 67
        y: 283
        text: qsTr("Telemetry")
        font.pointSize: 12
    }

    Label {
        id: label_intensity
        x: 67
        y: 187
        text: qsTr("Intensity")
        font.pointSize: 12
    }

    Label {
        id: label_phase
        x: 67
        y: 221
        text: qsTr("Phase")
        font.pointSize: 12
    }

    Rectangle {
        id: item_fourier
        x: 253
        y: 128
        width: 90
        height: 25
        color: "#ffffff"

        TextInput {
            id: textInput_fourier
            objectName: "textInput_fourier"
            text: qsTr("9993")
            leftPadding: 4
            topPadding: 3
            anchors.fill: parent
            font.pixelSize: 12
        }
    }

    Rectangle {
        id: item_amplitude
        x: 253
        y: 159
        width: 90
        height: 25
        color: "#ffffff"

        TextInput {
            id: textInput_amplitude
            objectName: "textInput_amplitude"
            text: qsTr("9994")
            anchors.fill: parent
            font.pixelSize: 12
            leftPadding: 4
            topPadding: 3
        }
    }

    Rectangle {
        id: item_intensity
        x: 253
        y: 190
        width: 90
        height: 25
        color: "#ffffff"

        TextInput {
            id: textInput_intensity
            objectName: "textInput_intensity"
            text: qsTr("9997")
            anchors.fill: parent
            font.pixelSize: 12
            leftPadding: 4
            topPadding: 3
        }
    }

    Rectangle {
        id: item_phase
        x: 253
        y: 221
        width: 90
        height: 25
        color: "#ffffff"

        TextInput {
            id: textInput_phase
            objectName: "textInput_phase"
            text: qsTr("9998")
            anchors.fill: parent
            font.pixelSize: 12
            leftPadding: 4
            topPadding: 3
        }
    }

    Rectangle {
        id: item_raw_frame
        x: 253
        y: 252
        width: 90
        height: 25
        color: "#ffffff"

        TextInput {
            id: textInput_raw_frame
            objectName: "textInput_raw_frame"
            text: qsTr("9995")
            anchors.fill: parent
            font.pixelSize: 12
            leftPadding: 4
            topPadding: 3
        }
    }

    Rectangle {
        id: item_telemetry
        x: 253
        y: 283
        width: 90
        height: 25
        color: "#ffffff"

        TextInput {
            id: textInput_telemetry
            objectName: "textInput_telemetry"
            text: qsTr("9996")
            anchors.fill: parent
            font.pixelSize: 12
            leftPadding: 4
            topPadding: 3
        }
    }

    Label {
        id: label_frame_server
        x: 67
        y: 369
        text: qsTr("Frame Server")
        font.pointSize: 12
    }

    Label {
        id: label_command_server
        x: 67
        y: 398
        text: qsTr("Command Server")
        font.pointSize: 12
    }

    Label {
        id: label_telmetry_server
        x: 67
        y: 427
        text: qsTr("Telemetry Server")
        font.pointSize: 12
    }

    Rectangle {
        id: item_frame_server
        x: 253
        y: 368
        width: 90
        height: 25
        color: "#848080"

        TextInput {
            id: textInput_frame_server
            objectName: "textInput_frame_server"
            text: qsTr("2000")
            anchors.fill: parent
            font.pixelSize: 12
            leftPadding: 4
            topPadding: 3
        }
    }

    Rectangle {
        id: item_command_server
        x: 253
        y: 399
        width: 90
        height: 25
        color: "#ffffff"

        TextInput {
            id: textInput_command_server
            objectName: "textInput_command_server"
            text: qsTr("2001")
            anchors.fill: parent
            font.pixelSize: 12
            leftPadding: 4
            topPadding: 3
        }
    }

    Rectangle {
        id: item_telemetry_server
        x: 253
        y: 430
        width: 90
        height: 25
        color: "#848080"

        TextInput {
            id: textInput_telemetry_server
            objectName: "textInput_telemetry_server"
            text: qsTr("2002")
            anchors.fill: parent
            font.pixelSize: 12
            leftPadding: 4
            topPadding: 3
        }
    }

    Button {
        id: button_apply
        objectName: "button_apply"
        x: 76
        y: 493
        text: qsTr("Apply")
    }

    Button {
        id: button_cancel
        objectName: "button_cancel"
        x: 221
        y: 493
        text: qsTr("Cancel")

        onClicked: {
            dhmx_port.visible = false
        }
    }


}















/*##^## Designer {
    D{i:12;anchors_height:20;anchors_width:80}D{i:14;anchors_height:20;anchors_width:80}
D{i:16;anchors_height:20;anchors_width:80}D{i:18;anchors_height:20;anchors_width:80}
D{i:20;anchors_height:20;anchors_width:80}D{i:22;anchors_height:20;anchors_width:80}
D{i:27;anchors_height:20;anchors_width:80}D{i:29;anchors_height:20;anchors_width:80}
D{i:31;anchors_height:20;anchors_width:80}
}
 ##^##*/
