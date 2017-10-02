#!/bin/bash

mkdir -p monthly_rebuilds
cd monthly_rebuilds
mkdir -p monthlies
mkdir -p logs
mkdir -p formations
mkdir -p clean
cd monthlies
monthlies_folder=`date +%m`"_"`date +%d`"_"`date +%Y`
mkdir -p $monthlies_folder

cd ../clean
clean_folder=`date +%m`"_"`date +%Y`
mkdir -p $clean_folder

