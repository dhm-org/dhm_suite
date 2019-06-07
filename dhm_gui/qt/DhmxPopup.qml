import QtQuick 2.6
import QtQuick.Window 2.2
import QtQuick.Controls 2.3
import QtQuick.Extras 1.4
import QtQuick.Layouts 1.3

Popup{
    property string popupText: "Sample text area for popupw window.  This area will be populated with text for an error"
    property string popupType: "ERROR"
    property int xPos: 0
    property int yPos: 0
    id: popup_dhmxRecon
    x: xPos
    y: yPos
    width: 350
    height: 250
    modal: true
    focus: true

    Rectangle{
        id: bg
        anchors.fill: parent
        color: "#c1bebe"
    }

    Label{
        x: 120
        y: 39
        text: popupType
        font.bold: true
        font.pointSize: 17
    }

    TextArea{
        x: 42
        y: 70
        width: 266
        height: 83
        text: popupText
        wrapMode: Text.WordWrap

        }
        Button{
            id: button_okay
            x: 109
            y: 167
            text: "Okay"

            onClicked: {
                popup_dhmxRecon.close()
            }
        }



    //closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
}
