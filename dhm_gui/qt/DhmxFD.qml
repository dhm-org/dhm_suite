
import QtQuick.Dialogs 1.0
import QtQuick 2.3 //2.7 2
import QtQuick.Window 2.2
import QtQuick.Controls 2.3 //need 2 1.4
import QtQuick.Extras 1.4

Item {
    ApplicationWindow{
        id: fd_win
        objectName: "fd_win"

        FileDialog{
            signal qml_signal_send_file_path
            id: dhmx_fd
            objectName: "dhmx_fd"
            title: "DEFAULT"
            //folder: shortcuts.home

            //property string file_path: ""

            onAccepted: {
                qml_signal_send_file_path()
                console.log("QML accepting, sending to python...")
                // dhmx_fd.file_path = dhmx_fd.fileUrls
                //qml_signal_send_file_path(dhmx_fd.fileUrls)
                //  dhmx_fd.close()
            }
            onRejected: {
                console.log("Cancelled filedialog")
                //dhmx_fd.close()
            }
            Component.onCompleted: visible = true
        }
        function open_file_dialog(dir){
            console.log("opening window...")
            dhmx_fd.folder = dir
            dhmx_fd.open()
        }
    }

}
