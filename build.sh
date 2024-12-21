#!/bin/bash

if ! command -v docker &> /dev/null
then
    echo "Docker не найден. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose не найден. Установите Docker Compose и попробуйте снова."
    exit 1
fi

echo "Сборка и запуск контейнеров..."
docker-compose up --build
