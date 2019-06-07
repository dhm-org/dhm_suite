import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.0

MouseArea {
    signal pack_cmd(string cmd)

    id: dhmx_about
    visible: true
    width: 500
    height: 250
    drag.target: dhmx_about
    transformOrigin: Item.TopLeft
    property string version: "v0.0.0"

    Rectangle {
        id: drag_area
        anchors.fill: parent

        color: "#c1bebe"
        border.color: "#242424"
        border.width: 4

        Image {
            id: image
            x: 99
            y: 17
            width: 302
            height: 100
            source: "images/dhmx_blk.png"
        }

        Button {
            id: button_close
            x: 200
            y: 191
            text: qsTr("Close")

            onClicked: {
                dhmx_about.visible = false
            }
        }

        Label {
            id: label_build
            x: 148
            y: 149
            text: qsTr("Build:")
        }

        Label {
            id: label_version_str
            x: 199
            y: 149
            text: dhmx_about.version
        }

        Label {
            id: label_authors
            x: 129
            y: 131
            text: qsTr("Authors:")
        }

        Label {
            id: label_author_names
            x: 199
            y: 131
            text: qsTr("Frank Lima, Felipe Fregoso")
        }
    }
}
