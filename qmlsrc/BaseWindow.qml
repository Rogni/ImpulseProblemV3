import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Window 2.2

Window {

    signal windowClosed()
    onClosing: {windowClosed()}
}
