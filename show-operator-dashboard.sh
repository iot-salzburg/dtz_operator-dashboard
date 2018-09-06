#!/usr/bin/env bash
echo "Printing 'docker service ls | grep op:"
docker service ls | grep op
echo ""
echo "Printing 'docker stack ps op':"
docker stack ps op
