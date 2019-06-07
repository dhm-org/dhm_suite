import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3
import QtMultimedia 5.8


MouseArea {
    signal pack_cmd(string cmd)

    id: dhmx_playback
    visible: true
    width: 650
    height: 700
    drag.target: dhmx_playback
    transformOrigin: Item.TopLeft
    property int prev_mouse_pos_x: 0

    Rectangle {
        id: drag_area
        anchors.fill: parent

        color: "#c1bebe"
        border.color: "#242424"
        border.width: 4
    }

    /* Scaling handle */
    Button{
        id: button_resize
        x: 617
        y: 667
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
                dhmx_playback.scale += cur_mouse_pos / 1024
            }
        }
    }

    Button {
        id: button_play
        x: 275
        y: 605
        text: qsTr("Button")
        display: AbstractButton.IconOnly
        icon.source: "images/icon_play.png"
        icon.width: 32
        icon.height: 32
        visible: true
        onClicked: {
            video.play()
            button_stop.visible = true
            button_play.visible = false
        }
    }
    Button {
        id: button_stop
        x: 275
        y: 605
        text: qsTr("Button")
        display: AbstractButton.IconOnly
        icon.source: "images/icon_stop.png"
        icon.width: 32
        icon.height: 32
        visible: false
        onClicked: {
            video.pause()
            button_stop.visible = false
            button_play.visible=  true
        }
    }

    Button {
        id: button_forward
        x: 388
        y: 605
        text: qsTr("Button")
        display: AbstractButton.IconOnly
        icon.source: "images/icon_fastforward.png"
        icon.width: 32
        icon.height: 32
        onPressed: {
            video.seek(video.position + 500)
        }
    }

    Button {
        id: button_reverse
        x: 163
        y: 605
        text: qsTr("Button")
        display: AbstractButton.IconOnly
        icon.source: "images/icon_reverse.png"
        icon.width: 32
        icon.height: 32
        onPressed: {
            video.seek(video.position - 500)
        }

    }

    Slider {
        id: slider
        y: 559
        height: 40
        //to: 1.4
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.left: parent.left
        anchors.leftMargin: 8
        value: 0.0
        Component.onCompleted: {
            slider.to = video.duration
        }
        onPressedChanged: {
            video.seek(slider.position*slider.to)
        }
    }

    Button {
        id: button_close
        x: 506
        y: 652
        text: qsTr("Close")
        anchors.right: parent.right
        anchors.rightMargin: 44
        onClicked: {
            dhmx_playback.visible = false
        }
    }

    Timer {
        id: playback_timer
        interval: 500
        repeat: true
        onTriggered: {
           if(!slider.pressed)
               slider.value = video.position

        }
    }


    Video {
        id: video
        x: 75
        y: 37
        width: 500
        height: 500
        //autoPlay: true
        autoLoad: true
        //seekable: true
        z:30
        //source: "../sample.avi"
        loops: MediaPlayer.Infinite
        Component.onCompleted: video.pause() //this is just so we can see a preview of the first frame
        onPlaying: {
            playback_timer.running = true
            slider.to = video.duration

        }
        onStopped: {
            playback_timer.running = false
        }
    }
}
