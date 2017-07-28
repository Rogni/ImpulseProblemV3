import QtQuick 2.0
import QtQuick.Controls 2.1

Page {
    id: root
    property var model: []
    property alias headerTitle: headerLabel.text
    property string leftString: "x%1"
    header: HeaderLabel {
        id: headerLabel
    }
    ListView {
        id: listView
        clip: true
        anchors.fill: parent
        model: root.model
        delegate: Item {
            width: root.width
            height: 40
            Label {
                id: label
                text: leftString.arg(index + 1) + " = "
                anchors.left: parent.left
                anchors.margins: 8
                anchors.verticalCenter: parent.verticalCenter
            }
            TextField {
                selectByMouse: true
                height: 36
                anchors.left: label.right
                anchors.right: parent.right
                anchors.margins: 8
                text: modelData.right
                onTextChanged: {
                    root.model[index].right = text
                }

                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}


