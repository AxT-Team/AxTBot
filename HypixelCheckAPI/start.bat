@echo off
title AxTPublic-HypixelCheckAPI
:start
php -S 0.0.0.0:30001
timeout /t 10 /nobreak
goto start