import QtQuick 2.6 //2.7 2
import QtQuick.Window 2.2
import QtQuick.Controls 2.3 //need 2 1.4
import QtQuick.Extras 1.4
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.1

ApplicationWindow {
    id: dhmx_win
    objectName: "dhmx_win"
    visible: true
    width: 1920
    height: 1080
    color: "black"
    title: qsTr("DHMX")
    visibility: Window.Maximized

    minimumWidth: 1200

    /* VERSION STRING */
    /* Set by Python in Main Window */
    property string version: ""
    /* * * * * * * * */

    property int dhmxCameraZ: 1
    property int dhmxCmdZ: 1
    property int dhmxConfZ: 1
    property int dhmxHoloDisplayZ: 1
    property int dhmxReconZ: 1

    property double universal_scale: 0.75

    signal qml_signal_close()


    onClosing: {
        close.accepted = false
        qml_signal_close()
    }

    onWidthChanged: {
        if(width < 1800){
            status.smallMode()
        }
        else{
            status.bigMode()
        }
    }

    Popup{
        id: popup
        property string popup_text: "Sample Text"
        width: 350
        height: 110
        modal: true
        focus: true
        x: Math.round((parent.width - width)/2)
        y: Math.round((parent.height - height)/2)
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        background: Rectangle {
            anchors.fill: parent
            color: "#c1bebe"
            border.color: "#242424"
            border.width: 4
        }

        ColumnLayout{

            anchors.fill: parent

            Text{
                width: popup.width - 10
                text: popup.popup_text
                wrapMode: Text.WrapAnywhere
            }

            /* For single confirmation-only popup dialogs */

            Button{
                Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                text: "Okay"
                onClicked: {
                    popup.close()
                }
            }
        }
    }

    header: ToolBar {
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 0

        RowLayout {
            anchors.fill:parent

            /* Sessions */
            Column {
                padding: 0
                Row{
                    padding: 5
                    spacing: session_title.width / 2 - 40
                    //leftPadding: 10
                    id: session
                    ToolButton {
                        id: new_session
                        signal qml_signal_new_session()
                        objectName: "toolbutton_new_session"
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "New Session"

                        Image {
                            source:"images/icon_new_session.png"
                            anchors.fill:parent
                            Rectangle {
                                id: session_bg
                                anchors.fill:parent
                                color: "#EFEFEF" //OS Color
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: session_border
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked: {
                            menu_new_session.onToolBar()
                        }
                        function setSelected(){
                            session_bg.gradient = grad_hover
                            session_border.color = "dark gray"
                        }
                        function setUnselected(){
                            session_bg.gradient = null
                            session_border.color = "#00000000"
                        }
                        enabled: true

                    }



                    ToolButton {
                        id: open_session
                        signal qml_signal_open_session()
                        objectName: "toolbutton_open_session"
                        x: 64
                        y: 0
                        width:35
                        height:35
                        ToolTip.visible: hovered
                        ToolTip.text: "Open Session"

                        Image {
                            source: "images/icon_load_session.png"
                            anchors.fill:parent
                            Rectangle {
                                id: open_session_bg
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: open_session_border
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked: {
                            qml_signal_open_session()
                        }
                        function onMenuBar(){
                            qml_signal_open_session()
                        }
                        function setSelected(){
                            open_session_bg.gradient = grad_hover
                            open_session_border.color = "dark gray"
                        }
                        function setUnselected(){
                            open_session_bg.gradient = null
                            open_session_border.color = "#00000000"
                        }
                        enabled: true
                    }
                }

                Item{
                    id: session_title
                    width: 135
                    height: 15
                    x:20 //totally subjective magic number just to align the text

                    Text {
                        x: 33
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: qsTr("Sessions")
                        anchors.verticalCenterOffset: -1
                        anchors.horizontalCenterOffset: -25
                        font.pointSize: 12
                        font.family: "arial"
                    }
                }
            }


            /* SEPERATOR */
            Column{
                ToolButton {
                    icon.source: "images/icon_seperator.png"
                }
                enabled: false
            }


            /* Framesource */
            Column {
                padding: 5
                Row{
                    objectName: "framesource"
                    padding: 5
                    spacing: framesource_title.width / 2 - 40
                    ///////leftPadding: 10
                    id: framesource_camera
                    ToolButton {
                        id: camera
                        signal qml_signal_camera()
                        objectName: "toolbutton_camera"
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Camera as framesource"
                        Image {
                            source: "images/icon_framesource_camera.png"
                            anchors.fill:parent
                            Rectangle {
                                id: camera_settings_bg
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: camera_settings_border
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_camera_server.onToolbar()
                        }
                        function setSelected(){
                            camera_settings_bg.gradient = grad_hover
                            camera_settings_border.color = "dark gray"
                        }
                        function setUnselected(){
                            camera_settings_bg.gradient = null
                            camera_settings_border.color = "#00000000"
                        }

                        enabled: true

                    }



                    ToolButton {
                        id: framesource_hologram
                        signal qml_signal_select_camera()
                        objectName: "toolbutton_framesource_hologram"
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Hologram as Framesource"
                        Image {
                            source: "images/icon_framesource_hologram.png"
                            anchors.fill:parent
                            Rectangle {
                                id: select_camera_bg
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: select_camera_border
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_hologram.onToolbar()
                        }
                        function setSelected(){
                            select_camera_bg.gradient = grad_hover
                            select_camera_border.color = "dark gray"
                        }
                        function setUnselected(){
                            select_camera_bg.gradient = null
                            select_camera_border.color = "#00000000"
                        }

                        enabled: true
                    }

                    ToolButton {
                        id: framesource_sequence
                        signal qml_signal_select_camera()
                        objectName: "toolbutton_framesource_sequence"
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Sequence"
                        Image {
                            source: "images/icon_framesource_sequence.png"
                            anchors.fill:parent
                            Rectangle {
                                id: framesource_sequence_bg
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: framesource_sequence_border
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_to_disk.onToolbar()
                        }
                        function setSelected(){
                            framesource_sequence_bg.gradient = grad_hover
                            framesource_sequence_border.color = "dark gray"
                        }
                        function setUnselected(){
                            framesource_sequence_bg.gradient = null
                            framesource_sequence_border.color = "#00000000"
                        }

                        enabled: true
                    }
                    function setSelected(which){
                        if(which == 1){
                            camera.setSelected()
                            framesource_hologram.setUnselected()
                            framesource_sequence.setUnselected()
                        }
                        if(which == 2){
                            camera.setUnselected()
                            framesource_hologram.setSelected()
                            framesource_sequence.setUnselected()
                        }
                        if(which == 3){
                            camera.setUnselected()
                            framesource_hologram.setUnselected()
                            framesource_sequence.setSelected()
                        }
                    }
                }

                Item{
                    id: framesource_title
                    width: 130
                    height: 15
                    x:15 //totally subjective magic number just to align the text
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: qsTr("Framesource")
                        anchors.verticalCenterOffset: 1
                        anchors.horizontalCenterOffset: 0
                        font.pointSize: 12
                        font.family: "arial"

                    }
                }
            }


            /* SEPERATOR */
            Column{
                ToolButton {
                    icon.source: "images/icon_seperator.png"
                }
                enabled: false
            }


            /* MODES */
            Column {
                padding: 5
                Row{
                    padding: 5
                    spacing: view_title.width / 2 - 50
                    id: modes
                    objectName: "modes"

                    /* Hologram */
                    ToolButton {
                        id: hologram_mode
                        objectName: "toolbutton_mode_camera"
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Hologram Only"
                        Image {
                            source: "images/icon_mode_hologram.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_hologram_mode
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_hologram_mode
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_holograms_only.onToolbar()
                        }
                        function setSelected(){
                            bg_hologram_mode.gradient = grad_hover
                            border_hologram_mode.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_hologram_mode.gradient = null
                            border_hologram_mode.color = "#00000000"
                        }

                        enabled: true

                    }


                    /* Amplitude */
                    ToolButton {
                        id: ampltidue_mode
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Amplitude Mode"
                        objectName: "toolbutton_mode_amplitude"
                        Image {
                            source: "images/icon_mode_amplitude.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_ampltidue_mode
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_ampltidue_mode
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_amplitude.onToolbar()
                        }
                        function setSelected(){
                            bg_ampltidue_mode.gradient = grad_hover
                            border_ampltidue_mode.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_ampltidue_mode.gradient = null
                            border_ampltidue_mode.color = "#00000000"
                        }

                        enabled: true
                    }

                    ToolButton {
                        id: intensity_mode
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Intensity Mode"
                        objectName: "toolbutton_mode_intensity"
                        Image {
                            source: "images/icon_mode_intensity.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_intensity_mode
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_intensity_mode
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_intensity.onToolbar()
                        }
                        function setSelected(){
                            bg_intensity_mode.gradient = grad_hover
                            border_intensity_mode.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_intensity_mode.gradient = null
                            border_intensity_mode.color = "#00000000"
                        }

                        enabled: true
                    }

                    /* PHASE */
                    ToolButton {
                        id: phase_mode
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Phase Mode"
                        objectName: "toolbutton_mode_phase"
                        Image {
                            source: "images/icon_mode_phase.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_phase_mode
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_phase_mode
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_phase.onToolbar()
                        }
                        function setSelected(){
                            bg_phase_mode.gradient = grad_hover
                            border_phase_mode.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_phase_mode.gradient = null
                            border_phase_mode.color = "#00000000"
                        }


                        enabled: true
                    }
                    function setSelected(which){
                        if(which == 1){
                            hologram_mode.setSelected()
                            ampltidue_mode.setUnselected()
                            intensity_mode.setUnselected()
                            phase_mode.setUnselected()

                        }
                        if(which == 2){
                            hologram_mode.setUnselected()
                            ampltidue_mode.setSelected()
                            intensity_mode.setUnselected()
                            phase_mode.setUnselected()
                        }
                        if(which == 3){
                            hologram_mode.setUnselected()
                            ampltidue_mode.setUnselected()
                            intensity_mode.setSelected()
                            phase_mode.setUnselected()
                        }
                        if(which == 4){
                            hologram_mode.setUnselected()
                            ampltidue_mode.setUnselected()
                            intensity_mode.setUnselected()
                            phase_mode.setSelected()
                        }
                        /* Below are special modes for combinations */
                        /* Amplitude & Phase */
                        if(which == 5){
                            hologram_mode.setUnselected()
                            ampltidue_mode.setSelected()
                            intensity_mode.setUnselected()
                            phase_mode.setSelected()
                        }
                        /* Intensity & Phase */
                        if(which == 6){
                            hologram_mode.setUnselected()
                            ampltidue_mode.setUnselected()
                            intensity_mode.setSelected()
                            phase_mode.setSelected()
                        }
                        /* All */
                        if(which == 7){
                            hologram_mode.setSelected()
                            ampltidue_mode.setSelected()
                            intensity_mode.setSelected()
                            phase_mode.setSelected()
                        }
                    }

                }

                Item{
                    id: mode_title
                    width: 130
                    height: 15
                    x:15 //totally subjective magic number just to align the text
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: qsTr("Mode")
                        anchors.verticalCenterOffset: 1
                        anchors.horizontalCenterOffset: 13
                        font.pointSize: 12
                        font.family: "arial"

                    }
                }
            }


            /* SEPERATOR */
            Column{
                ToolButton {
                    icon.source: "images/icon_seperator.png"
                }
                enabled: false
            }



            /* DISPLAY */
            Column {
                padding: 5
                Row{
                    padding: 5
                    spacing: view_title.width / 2 - 50
                    id: view

                    /* Hologram */
                    ToolButton {
                        id: hologram
                        objectName: "toolbutton_display_hologram"
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Hologram"
                        Image {
                            source: "images/icon_hologram.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_hologram
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_hologram
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_view_hologram.onToolbar()
                        }
                        function setSelected(){
                            bg_hologram.gradient = grad_hover
                            border_hologram.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_hologram.gradient = null
                            border_hologram.color = "#00000000"
                        }

                        enabled: true

                    }


                    /* Amplitude */
                    ToolButton {
                        id: ampltidue
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Amplitude"
                        objectName: "toolbutton_display_amplitude"
                        Image {
                            source: "images/icon_amplitude.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_amplitude
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_amplitude
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_view_amplitude.onToolbar()
                        }
                        function setSelected(){
                            bg_amplitude.gradient = grad_hover
                            border_amplitude.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_amplitude.gradient = null
                            border_amplitude.color = "#00000000"
                        }

                        enabled: true
                    }

                    ToolButton {
                        id: intensity
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Intensity"
                        objectName: "toolbutton_display_intensity"
                        Image {
                            source: "images/icon_intensity.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_intensity
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_intensity
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_view_intensity.onToolbar()
                        }
                        function setSelected(){
                            bg_intensity.gradient = grad_hover
                            border_intensity.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_intensity.gradient = null
                            border_intensity.color = "#00000000"
                        }

                        enabled: true
                    }

                    /* PHASE */
                    ToolButton {
                        id: phase
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Phase"
                        objectName: "toolbutton_display_phase"
                        Image {
                            source: "images/icon_phase.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_phase
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_phase
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_view_phase.onToolbar()
                        }
                        function setSelected(){
                            bg_phase.gradient = grad_hover
                            border_phase.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_phase.gradient = null
                            border_phase.color = "#00000000"
                        }

                        enabled: true
                    }


                    /* FOURIER */
                    ToolButton {
                        id: fourier
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Fourier"
                        objectName: "toolbutton_display_fourier"
                        Image {
                            source: "images/icon_fourier.png"
                            anchors.fill:parent
                            Rectangle {
                                id: bg_fourier
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: border_fourier
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked:{
                            menu_view_fourier.onToolbar()
                        }
                        function setSelected(){
                            bg_fourier.gradient = grad_hover
                            border_fourier.color = "dark gray"
                        }
                        function setUnselected(){
                            bg_fourier.gradient = null
                            border_fourier.color = "#00000000"
                        }

                        enabled: true
                    }

                }

                Item{
                    id: view_title
                    width: 130
                    height: 15
                    x:15 //totally subjective magic number just to align the text
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: qsTr("Views")
                        anchors.verticalCenterOffset: 1
                        anchors.horizontalCenterOffset: 54
                        font.pointSize: 12
                        font.family: "arial"

                    }
                }
            }


            /* SEPERATOR */
            Column{
                ToolButton {
                    icon.source: "images/icon_seperator.png"
                }
                enabled: false
            }


            /* Run / Idle */
            Column {
                id: run_idle
                padding: 5
                Row{
                    id: run_and_idle
                    objectName: "run_and_idle"
                    padding: 5
                    spacing: run_idle_title.width / 2 - 40
                    //////leftPadding: 10
                    ToolButton {
                        id: run
                        signal qml_signal_run()
                        objectName: "toolbutton_run"
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Stream/Run Framesource"
                        // anchors.horizontalCenter: schedule_management.horizontalCenter
                        Image {
                            source: "images/icon_run.png"
                            anchors.fill:parent
                            Rectangle {
                                id: run_bg
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: run_border
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked: {
                            menu_run.onToolbar()
                        }
                        function setSelected(){
                            run_bg.gradient = grad_hover
                            run_border.color = "dark gray"
                        }
                        function setUnselected(){
                            run_bg.gradient = null
                            run_border.color = "#00000000"
                        }
                        enabled: true

                    }

                    ToolButton {
                        id: idle
                        signal qml_signal_idle()
                        objectName: "toolbutton_idle"
                        width: 35
                        height: 35
                        ToolTip.visible: hovered
                        ToolTip.text: "Set Streaming to Idle"
                        Image {
                            source: "images/icon_idle.png"
                            anchors.fill:parent
                            Rectangle {
                                id: idle_bg
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -1
                            }
                            Rectangle{
                                anchors.fill:parent
                                color: "#EFEFEF"
                                radius: 3
                                z: -2
                            }

                            Rectangle{
                                id: idle_border
                                color: "#00000000"
                                width: parent.width+2
                                height: parent.height+2
                                x: parent.x - 1
                                y: parent.y - 1
                                radius: 3
                                z: -3
                            }
                        }
                        onClicked: {
                            menu_idle.onToolbar()
                        }
                        function setSelected(){
                            idle_bg.gradient = grad_hover
                            idle_border.color = "dark gray"
                        }
                        function setUnselected(){
                            idle_bg.gradient = null
                            idle_border.color = "#00000000"
                        }

                        enabled: true
                    }
                    function setSelected(which){
                        /* Run */
                        if(which == 1){
                            run.setSelected()
                            idle.setUnselected()
                        }
                        /* Idle */
                        if(which == 2){
                            run.setUnselected()
                            idle.setSelected()
                        }
                        /* Special third state to unset both */
                        if(which == 3){
                            run.setUnselected()
                            idle.setUnselected()
                        }
                    }
                }

                Item{
                    id: run_idle_title
                    width: 135
                    height: 15
                    x:17 //totally subjective magic number just to align the text
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: qsTr("Run & Idle")
                        anchors.verticalCenterOffset: 1
                        anchors.horizontalCenterOffset: -31
                        font.pointSize: 12
                        font.family: "arial"
                    }
                }
            }


            /* SEPERATOR */
            Column{
                ToolButton {
                    icon.source: "images/icon_seperator.png"
                }
                enabled: false
            }


            /* Server & Heartbeat Status */
            Column{
                Item{
                   id: status
                   x: 900
                   y: 10

                   function smallMode(){
                       x = -290
                       y = 80

                       text_controller_status.color = "white"
                       text_datalogger_status.color = "white"
                       text_framesource_status.color = "white"
                       text_gui_server_status.color = "white"
                       text_reconstructor_status.color = "white"
                       text_heartbeat_status.color = "white"
                   }
                   function bigMode(){
                       x = 900
                       y = 10

                       text_controller_status.color = "black"
                       text_datalogger_status.color = "black"
                       text_framesource_status.color = "black"
                       text_gui_server_status.color = "black"
                       text_reconstructor_status.color = "black"
                       text_heartbeat_status.color = "black"
                   }

                Item{
                    /* all of this position is just for "feel good" looks */
                    id: heartbeat_status
                    x: 300

                    Image{
                        id: icon_heartbeat_status
                        x: 0
                        y: 2
                        objectName: "icon_heartbeat_status"

                        // The reset flag that python checks to see if timer is expired
                        property bool reset: false

                        source: "images/icon_status_caution.png"
                        width:20
                        height:20

                        function armTimer(millisec){
                            heartbeat.interval = millisec
                            heartbeat.running = true
                            heartbeat.repeat = false
                            icon_heartbeat_status.reset = false
                            icon_heartbeat_status.source = "images/icon_status_good.png"
                        }
                        function resetTimer(){
                            icon_heartbeat_status.source = "images/icon_status_good.png"
                            icon_heartbeat_status.reset = false
                            heartbeat.restart()
                        }

                        function timerExpire(){
                            heartbeat.stop()
                        }

                        function setMode(mode){
                            source = globalSetStatusMode(mode)
                        }
                        Timer{
                            id:heartbeat
                            running: false
                            interval: 3500 //3 seconds default

                            onTriggered: {
                                icon_heartbeat_status.source = "images/icon_status_bad.png"
                                icon_heartbeat_status.reset = true
                            }
                        }
                    }
                    Text{
                        id: text_heartbeat_status
                        text: "Heartbeat Status"
                        font.family: "arial"
                        font.pointSize: 12
                        x: icon_heartbeat_status.width + 10 //10 for padding
                        y: 3
                        height: 20

                    }
                }

                Item{
                    /* all of this position is just for "feel good" looks */
                    id: datalogger_status
                    x: 300
                    y: 25

                    Image{
                        id: icon_datalogger_status
                        x: 0
                        y: 2
                        objectName: "icon_datalogger_status"
                        source: "images/icon_status_caution.png"
                        width:20
                        height:20
                        function setMode(mode){
                            source = globalSetStatusMode(mode)
                        }
                    }
                    Text{
                        id: text_datalogger_status
                        text: "Datalogger Status"
                        font.family: "arial"
                        font.pointSize: 12
                        x: icon_heartbeat_status.width + 10 //10 for padding
                        y: 3
                        height: 20

                    }
                }

                Item{
                    /* all of this position is just for "feel good" looks */
                    id: controller_status
                    x: heartbeat_status.x + 200

                    Image{
                        id: icon_controller_status
                        x: 0
                        y: 2
                        objectName: "icon_controller_status"
                        source: "images/icon_status_caution.png"
                        width:20
                        height:20
                        function setMode(mode){
                            source = globalSetStatusMode(mode)
                        }
                    }
                    Text{
                        id: text_controller_status
                        text: "controller Status"
                        font.family: "arial"
                        font.pointSize: 12
                        x: icon_heartbeat_status.width + 10 //10 for padding
                        y: 3
                        height: 20
                    }
                }

                Item{
                    /* all of this position is just for "feel good" looks */
                    id: guiserver_status
                    x: datalogger_status.x + 200
                    y: 25

                    Image{
                        id: icon_guiserver_status
                        x: 0
                        y: 2
                        objectName: "icon_guiserver_status"
                        source: "images/icon_status_caution.png"
                        width:20
                        height:20
                        function setMode(mode){
                            source = globalSetStatusMode(mode)
                        }
                    }
                    Text{
                        id: text_gui_server_status
                        text: "GUI Server Status"
                        font.family: "arial"
                        font.pointSize: 12
                        x: icon_heartbeat_status.width + 10 //10 for padding
                        y: 3
                        height: 20
                    }
                }

                Item{
                    /* all of this position is just for "feel good" looks */
                    id: reconstructor_status
                    x: controller_status.x + 200

                    Image{
                        id: icon_reconstructor_status
                        x: 0
                        y: 2
                        objectName: "icon_reconstructor_status"
                        source: "images/icon_status_caution.png"
                        width:20
                        height:20
                        function setMode(mode){
                            source = globalSetStatusMode(mode)
                        }
                    }
                    Text{
                        id: text_reconstructor_status
                        text: "Reconstructor Status"
                        font.family: "arial"
                        font.pointSize: 12
                        x: icon_heartbeat_status.width + 10 //10 for padding
                        y: 3
                        height: 20
                    }
                }
                Item{
                    /* all of this position is just for "feel good" looks */
                    id: framesource_status
                    x: guiserver_status.x + 200
                    y: 25

                    Image{
                        id: icon_framesource_status
                        x: 0
                        y: 2
                        objectName: "icon_framesource_status"
                        source: "images/icon_status_caution.png"
                        width:20
                        height:20

                        function setMode(mode){
                            source = globalSetStatusMode(mode)
                        }
                    }
                    Text{
                        id: text_framesource_status
                        text: "Framesource Status"
                        font.family: "arial"
                        font.pointSize: 12
                        x: icon_heartbeat_status.width + 10 //10 for padding
                        y: 3
                        height: 20
                    }
                }


            }

            }//

            /* Fills remainder of the toolbar space so that icons are close together */
            Item {Layout.fillWidth: true }
        }
    }



    /* This is used for toolbar volumetric gradient backgrounds only */
    Item{
        Rectangle {
            visible: false
            gradient: Gradient {
                id: grad_select
                GradientStop { position: 0 ; color:  "#e3e5f9" }
                GradientStop { position: 1 ; color:  "#c7cbf4" }
            }
        }
        Rectangle {
            visible: false
            gradient: Gradient {
                id: grad_hover
                GradientStop { position: 0 ; color:  "#b0b0e0"}
                GradientStop { position: 1 ; color:  "#c0c0db" }
            }

        }
    }












    menuBar: MenuBar{
        /* FILE */
        Menu{
            title: "File"
            MenuItem {
                signal qml_signal_launch_configuration_window
                id: menu_new_session
                objectName: "menu_new_session"
                text: "New Session..."
                onTriggered: {
                    qml_signal_launch_configuration_window()
                    subwin_conf.visible = true
                    windowManager(subwin_conf)
                }
                function onToolBar(){
                    qml_signal_launch_configuration_window()
                    subwin_conf.visible = true
                    windowManager(subwin_conf)
                }
            }
            MenuItem {
                objectName: "menu_open_session"
                text: "Open Session..."
                enabled: true
                onClicked: {
                    open_session.onMenuBar()
                }
            }
            MenuItem {
                signal qml_signal_save_session
                objectName: "menu_save_session"
                text: "Save Session..."
                enabled: true
                /* Since no global signal exists for launching a save window via QML, a signal must be passed into python */
                onClicked: {
                    qml_signal_save_session()
                }
            }
            /* Commented out for a possible future feature addition */
//            MenuItem {
//                objectName: "menu_close_session"
//                text: "Close Session"
//                enabled: false
//            }
            MenuItem {
                signal qml_signal_quit
                objectName: "menu_exit"
                text: "Exit"
                onTriggered: {
                    qml_signal_quit()
                    //Qt.quit()
                }
            }
        }

        /* FRAME SOURCE */
        Menu{
            title: "Frame Source"
            MenuItem {
                signal qml_signal_camera_server
                id: menu_camera_server
                objectName: "menu_camera_server"
                text: "Camera Server"
                onTriggered: {
                    qml_signal_camera_server()
                }
                function onToolbar(){
                    qml_signal_camera_server()
                }
            }
            Menu{
                title: "File"
                MenuItem {
                    signal qml_signal_hologram_open_fd
                    id: menu_hologram
                    objectName: "menu_hologram"
                    text: "Hologram"

                    onTriggered: {
                        qml_signal_hologram_open_fd()
                    }
                    function onToolbar() {
                       qml_signal_hologram_open_fd()
                    }
                }
                MenuItem {
                        id: menu_to_disk
                        signal qml_signal_to_disk_open_fd
                        objectName: "menu_to_disk"
                        text: "Sequence"
                        onTriggered: {
                            qml_signal_to_disk_open_fd()
                        }
                        function onToolbar(){
                            qml_signal_to_disk_open_fd()
                        }
                }

            }
            MenuItem {
                objectName: "menu_remote_location"
                text: "Remote Location"
            }

            MenuSeparator{}

            MenuItem{
                signal qml_signal_run
                id: menu_run
                objectName: "menu_run"
                text: "Run"
                onTriggered: {
                    qml_signal_run()
                }
                function onToolbar(){
                    qml_signal_run()
                }
            }
            MenuItem{
                signal qml_signal_idle
                id: menu_idle
                objectName: "menu_idle"
                text: "Idle"
                onTriggered: {
                    qml_signal_idle()
                }
                function onToolbar(){
                    qml_signal_idle()
                }
            }
        }

        /* MODE */
        Menu{
            title: "Mode"
            MenuItem {
                signal qml_signal_holograms_only
                id: menu_holograms_only
                objectName: "menu_holograms_only"
                text: "Holograms Only"
                onTriggered: {
                    qml_signal_holograms_only()
                }
                function onToolbar(){
                    qml_signal_holograms_only()
                }
            }
            Menu{
                title: "Reconstruction"
                MenuItem {
                    id: menu_amplitude
                    signal qml_signal_reconst_amplitude
                    objectName: "menu_amplitude"
                    text: "Amplitude"
                    onTriggered: {
                        qml_signal_reconst_amplitude()
                    }
                    function onToolbar(){
                        qml_signal_reconst_amplitude()
                    }
                }
                MenuItem {
                    id: menu_intensity
                    signal qml_signal_reconst_intensity
                    objectName: "menu_intensity"
                    text: "Intensity"
                    onTriggered: {
                        qml_signal_reconst_intensity()
                    }
                    function onToolbar(){
                        qml_signal_reconst_intensity()
                    }
                }
                MenuItem {
                    id: menu_phase
                    signal qml_signal_reconst_phase
                    objectName: "menu_phase"
                    text: "Phase"
                    onTriggered: {
                        qml_signal_reconst_phase()
                    }
                    function onToolbar(){
                        qml_signal_reconst_phase()
                    }
                }
                MenuItem {
                    signal qml_signal_reconst_amplitude_and_phase
                    objectName: "menu_amplitude_and_phase"
                    text: "Amplitude and Phase"
                    onTriggered: {
                        qml_signal_reconst_amplitude_and_phase()
                    }
                }
                MenuItem {
                    signal qml_signal_reconst_intensity_and_phase
                    objectName: "menu_intensity_and_phase"
                    text: "Intensity and Phase"
                    onTriggered: {
                        qml_signal_reconst_intensity_and_phase()
                    }
                }
                MenuItem{
                    signal qml_signal_process_all
                    objectName: "menu_process_all"
                    text: "All"
                    onTriggered: {
                        qml_signal_process_all()
                    }
                }
            }
        }

        /* SETTINGS */
        Menu{
            title: "Settings"
            MenuItem {
                signal qml_signal_launch_reconstruction_window()
                objectName: "menu_reconstruction"
                text: "Reconstruction"
                onTriggered: {
                    subwin_recon.visible = true
                    windowManager(subwin_recon)
                    qml_signal_launch_reconstruction_window()
                }
            }
            MenuItem {
                id: menu_camera
                objectName: "menu_camera"
                signal qml_signal_launch_dhmxc()
                text: "Camera"
                enabled: true
                onTriggered: {
                    qml_signal_launch_dhmxc()
                }
                function onToolBar(){
                    qml_signal_launch_dhmxc()
                }
            }
            Menu{
                title: "Phase Unwrapping"
                enabled: false
                MenuItem {
                    objectName: "menu_algorithm_1"
                    text: "Algorithm 1"
                }
                MenuItem {
                    objectName: "menu_algorithm_2"
                    text: "Algorithm 2"
                }
                MenuItem {
                    objectName: "menu_algorithm_3"
                    text: "Algorithm 3"
                }
            }

        }

        /* OPTIONS */
        /* FML: 20190318 - disabled section, why have it if there's nothing? */
//        Menu{
//            title: "Options"
//            MenuItem { text: "NONE"}
//        }

        /* TOOLS */
        Menu{
            title: "Tools"
            MenuItem {
                signal qml_signal_launch_command_window()
                objectName: "menu_manual_control"
                text: "Manual Control..."
                onTriggered: {
                    qml_signal_launch_command_window()
                    subwin_cmd.visible = true
                    windowManager(subwin_cmd)
                }
            }
        }

        /* VIEW */
        Menu{
            title: "View"
            MenuItem {
                text: "Playback"
                enabled: false
                onTriggered: subwin_playback.visible = true
            }

            MenuItem {
                id: menu_view_hologram
                signal qml_signal_launch_holo_display()
                objectName: "menu_view_hologram"
                text: "Hologram"
                onTriggered: {
                    subwin_holo_display.visible = true
                    windowManager(subwin_holo_display)
                    subwin_holo_display.set_display("Hologram")
                    qml_signal_launch_holo_display()
                }
                function onToolbar(){
                    subwin_holo_display.visible = true
                    windowManager(subwin_holo_display)
                    subwin_holo_display.set_display("Hologram")
                    qml_signal_launch_holo_display()
                }
            }
            MenuItem {
                id: menu_view_fourier
                signal qml_signal_launch_fourier_display()
                objectName: "menu_view_fourier"
                text: "Fourier"
                onTriggered: {
                    subwin_fourier.visible = true
                    windowManager(subwin_fourier)
                    subwin_fourier.set_display("Fourier")
                    qml_signal_launch_fourier_display()
                }
                function onToolbar(){
                    subwin_fourier.visible = true
                    windowManager(subwin_fourier)
                    subwin_fourier.set_display("Fourier")
                    qml_signal_launch_fourier_display()
                }
            }
            MenuItem {
                id: menu_view_amplitude
                signal qml_signal_launch_amplitude_display()
                objectName: "menu_view_amplitude"
                text: "Amplitude"
                onTriggered: {
                    subwin_amplitude.visible = true
                    windowManager(subwin_amplitude)
                    subwin_amplitude.set_display("Amplitude")
                    qml_signal_launch_amplitude_display()
                }
                function onToolbar(){
                    subwin_amplitude.visible = true
                    windowManager(subwin_amplitude)
                    subwin_amplitude.set_display("Amplitude")
                    qml_signal_launch_amplitude_display()
                }
            }
            MenuItem {
                id: menu_view_phase
                signal qml_signal_launch_phase_display()
                objectName: "menu_view_phase"
                text: "Phase"
                onTriggered: {
                    subwin_phase.visible = true
                    windowManager(subwin_phase)
                    subwin_phase.set_display("Phase")
                    qml_signal_launch_phase_display()
                }
                function onToolbar(){
                    subwin_phase.visible = true
                    windowManager(subwin_phase)
                    subwin_phase.set_display("Phase")
                    qml_signal_launch_phase_display()
                }
            }
            MenuItem {
                id: menu_view_intensity
                signal qml_signal_launch_intensity_display()
                objectName: "menu_view_intensity"
                text: "Intensity"
                onTriggered: {
                    subwin_intensity.visible = true
                    windowManager(subwin_intensity)
                    subwin_intensity.set_display("Intensity")
                    qml_signal_launch_intensity_display()
                }
                function onToolbar(){
                    subwin_intensity.visible = true
                    windowManager(subwin_intensity)
                    subwin_intensity.set_display("Intensity")
                    qml_signal_launch_intensity_display()
                }
            }

        }

        /* WINDOW */
        Menu{
            title: "Window"
            enabled: false
            MenuItem { text: "Tile Horizontal"}
            MenuItem { text: "Tile Vertical"}
            MenuItem { text: "Cascade"}
            MenuItem { text: "1 Hologram"}
            MenuItem { text: "2 Phase"}
            MenuItem { text: "3 Amplitude"}
            MenuItem { text: "4 Fourier"}
            MenuItem { text: "5 Reconstruction Settins"}
        }

        /* HELP! */
        Menu{
            title: "Help"
            MenuItem {
                id: menu_about
                objectName: "menu_about"
                text: "About"
                signal qml_signal_launch_about()
                onTriggered: {
                    qml_signal_launch_about()
                    subwin_about.visible = true
                }
            }
        }
    }


    Rectangle{

        color:"#EFEFEF"
        anchors.fill:text_status
    }

    Text {
        id: text_status
        objectName: "text_status"
        y: 1080
        height: 20
        text: qsTr("Initialzing DHMx and DHMSW")
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
    }


    /* Subwindows here */
//    DhmxPort{
//        objectName: "subwin_port"
//        id: subwin_port
//        visible: false
//        z:65535
//    }

    DhmxAbout{
        objectName: "subwin_about"
        id: subwin_about
        visible: false
        z:65535 /* Always make it the top-most */
    }

    DhmxPlayback{
        objectName: "subwin_playback"
        id: subwin_playback
        visible: false
        z:1
    }

    DhmxConf{
        objectName: "subwin_conf"
        id: subwin_conf
        visible: false
        z: 1
        scale: universal_scale
        onPressed: {
            windowManager(subwin_conf)
        }
    }
    DhmxRecon{
        objectName: "subwin_recon"
        id: subwin_recon
        visible: false
        z: 1
        scale: universal_scale
        onPressed:  {
            windowManager(subwin_recon)
        }
    }
    DhmxHoloDisplay{
        objectName: "subwin_fourier"
        id: subwin_fourier
        visible: false
        z: 1
        scale: universal_scale
        onPressed: {
            windowManager(subwin_fourier)

        }
    }
    DhmxHoloDisplay{
        objectName: "subwin_holo_display"
        id: subwin_holo_display
        visible: false
        z: 1
        scale: universal_scale
        onPressed: {
            windowManager(subwin_holo_display)

        }
    }
    DhmxHoloDisplay{
        objectName: "subwin_phase"
        id: subwin_phase
        visible: false
        scale: universal_scale
        onPressed: {
            windowManager(subwin_phase)
        }
    }
    DhmxHoloDisplay{
        objectName: "subwin_intensity"
        id: subwin_intensity
        visible: false
        scale: universal_scale
        onPressed: {
            windowManager(subwin_intensity)
        }
    }
    DhmxHoloDisplay{
        objectName: "subwin_amplitude"
        id: subwin_amplitude
        visible: false
        scale: universal_scale
        onPressed:{
            windowManager(subwin_amplitude)
        }
    }

    DhmxCmd{
        objectName: "subwin_cmd"
        id: subwin_cmd
        visible: false
        z:1
        onPressed: {
            windowManager(subwin_cmd)
        }

    }

    Image {
        id: image
        anchors.fill: parent
        source: "images/bg2.jpg"
        opacity: 0.3
    }

    Image {
        id: image1
        x: 161
        y: 190
        width: 318
        height: 100
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        source: "images/dhmx.png"
    }

    Image {
        id: image2
        y: 1023
        width: 268
        height: 51
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 26
        anchors.left: parent.left
        anchors.leftMargin: 5
        antialiasing: false
        source: "images/nasa-jpl.png"
    }


    /* This FileDialog window is only used for coupling with commands for DHM */
    FileDialog{
        signal qml_signal_send_file_path(string path, string cmd, var id, int selection)
        id: dhmx_fd_cmd
        objectName: "dhmx_fd_cmd"
        title: "DEFAULT"

        //nameFilters: ["Image files (*.jpg *.png *.bmp *.tif)","All files (*)"]

        property string cmd_type: ""
        property var callback_id
        property int callback_selection

        onAccepted: {
            var path = dhmx_fd_cmd.fileUrl.toString();
            var cleanPath
            // remove prefixed "file:///"
            path = path.replace(/^(file:\/{2})/,"");

            // unescape html codes like '%23' for '#'
            cleanPath = decodeURIComponent(path);

            qml_signal_send_file_path(cleanPath, cmd_type,callback_id,callback_selection)

        }
        onRejected: {
            dhmx_fd_cmd.close()
        }
        Component.onCompleted: visible = false

    }


    /* This FileDialog window is a more generic type that is not used for coupling with commands */
    FileDialog{
        signal qml_signal_send_file_path(string path)
        id: dhmx_fd_generic
        objectName: "dhmx_fd_generic"
        title: "DEFAULT"
        nameFilters: ["Config files (*.cfg)","All files (*)"]

        onAccepted: {
            var path = dhmx_fd_generic.fileUrl.toString();
            var cleanPath
            // remove prefixed "file:///"
            path = path.replace(/^(file:\/{2})/,"");

            // unescape html codes like '%23' for '#'
            cleanPath = decodeURIComponent(path);
            qml_signal_send_file_path(cleanPath)

        }
        onRejected: {
            dhmx_fd_generic.close()
        }
        Component.onCompleted: visible = false

    }

//    Rectangle{
//        id: cover_bg
//        objectName: "cover_bg"
//        anchors.fill: parent
//        color: "#FFFFFF"
//    }


    /* This function opens a file dialog window but also passes in a command so that in the
     * PyQt side, the command is structured and sent */
    /* example: open_file_dialog('/home/qt','Please Select a File','framesource mode=') */
    /* New as of DHMx v0.9.0 -- there is a callback_id and callback_selection so that
     * a callback source can be used to traceback and set a value.  This functionality is
     * used for setting the toolbar icons.  You set the callback function as teh toolbar
     * icon setting function setSelected() and have the option to pass in an int selection
     * so that if there are any special mutually exclusive sets of buttons you can specify
     * the exact button to set and unset the rest */
    function open_file_dialog(title,cmd_type,one_or_many,select_folder,callback_id,callback_selection){
        if(!select_folder){
           dhmx_fd_cmd.nameFilters = ["Image files (*.jpg *.png *.bmp *.tif)","All files (*)"]
          // dhmx_fd.setNameFilters("Image files (*.jpg *.png *.bmp *.tif)","All files (*)")
        }
        else{
       //     dhmx_fd.nameFilters = "."
            dhmx_fd_cmd.nameFilters = ["All files (*)"]
        }

        dhmx_fd_cmd.setSelectMultiple(one_or_many)
        dhmx_fd_cmd.setSelectFolder(select_folder)
        dhmx_fd_cmd.title = title
        dhmx_fd_cmd.cmd_type = cmd_type
        dhmx_fd_cmd.callback_id = callback_id
        dhmx_fd_cmd.callback_selection = callback_selection
        dhmx_fd_cmd.open()
    }

    function globalSetStatusMode(mode){

        //Error Status
        if(mode < 0){
            return "images/icon_status_bad.png"
        }
        // Optimal Status
        else if(mode == 0){
            return "images/icon_status_good.png"
        }
        // Caution
        else if(mode > 0){
            return "images/icon_status_caution.png"
        }
        else{
            return "images/icon_status_bad.png"
        }
    }
    function windowManager(window){
        /* 9 is the highest level window - a.k.a the top. */
        window.focus = true
        window.z = 9

        if(window != subwin_cmd && subwin_cmd.z == 9 && subwin_cmd.z > 1){
            subwin_cmd.z -= 1
        }
        if(window != subwin_conf && subwin_conf.z == 9 && subwin_conf.z > 1){
            subwin_conf.z -= 1
        }
        if(window != subwin_holo_display && subwin_holo_display.z == 9 && subwin_holo_display.z > 1){
            subwin_holo_display.z -= 1
        }
        if(window != subwin_recon && subwin_recon.z == 9 && subwin_recon.z > 1){
            subwin_recon.z -= 1
        }
        if(window != subwin_phase && subwin_phase.z == 9 && subwin_phase.z > 1){
            subwin_phase.z -= 1
        }
        if(window != subwin_amplitude && subwin_amplitude.z == 9 && subwin_amplitude.z > 1){
            subwin_amplitude.z -= 1
        }
        if(window != subwin_fourier && subwin_fourier.z == 9 && subwin_fourier.z > 1){
            subwin_fourier.z -= 1
        }
    }


    function launch_popup(popup_text){
        popup.popup_text = popup_text
        popup.open()
        console.log("popup window launched. with text: ",popup_text)
    }

}









/*##^## Designer {
    D{i:116;anchors_width:350;anchors_x:800}
}
 ##^##*/
