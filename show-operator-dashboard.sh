#!/usr/bin/env bash
echo "Printing 'docker service ls | grep op_:"
docker service ls | grep op_
echo ""
echo "Printing 'docker stack ps op_':"
docker stack ps op_
