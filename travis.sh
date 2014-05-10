#! /bin/bash
export SUBLIME_TEXT_VERSION=$1
export PACKAGE="$2"
export STP=$HOME/.config/sublime-text-$SUBLIME_TEXT_VERSION/Packages

if [ -z $(which subl) ]; then
    if [ $SUBLIME_TEXT_VERSION -eq 2 ]; then
        echo installing sublime 2
        sudo add-apt-repository ppa:webupd8team/sublime-text-2 -y
        sudo apt-get update
        sudo apt-get install sublime-text -y
    elif [ $SUBLIME_TEXT_VERSION -eq 3 ]; then
        echo installing sublime 3
        sudo add-apt-repository ppa:webupd8team/sublime-text-3 -y
        sudo apt-get update
        sudo apt-get install sublime-text-installer -y
    fi
fi

if [ ! -d $STP ]; then
    echo creating sublime package directory
    mkdir -p $STP
fi

if [ ! -d $STP/$PACKAGE ]; then
    echo symlink the package to sublime package directory
    ln -s $PWD $STP/$PACKAGE
fi