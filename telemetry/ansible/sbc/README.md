# network-telemetry
Stack TICK para monitoreo y recoleccion de información de telemtría

### Automation scripts

#### Crontab

Hay dos modalidades para la ejecucion de los playbooks de ansible. A través de un script loop.py que queda en ejecución constante y es el encargado de la iteración y, de forma alternativa, descansar en cron para la iteración a través de network-telemetry.py.

En ambos casos, los scripts python son llamados desde cron a través de un bash script llamado start.sh. En el primer escenario, ese script monitorea que loop.py se este ejecutando correctamente. En el segundo, llama a network-telemetry.py para la ejecución del playbook. La ejecución del playbook se realiza a través de python por los siguientes motivos:

- Procesos zombies de ansible se limpian antes de una nueva ejecución para evitar memory leaks
- Generación de logs a filesystem para troubleshooting
- Limpieza de logs
- Posible interacción con apis (telegram, influx) para generar reportes

Cron config:
```
# m h  dom mon dow   command
*/3 * * * * /code/network-telemetry/ansible/sbc/scripts/start.sh
0 0 */2 * * rm /code/network-telemetry/ansible/sbc/log/*.log 
```

#### network-telemetry
Script que consulta si se esta ejecutando un proceso con el script loop.py. Si se esta ejecutando no hará nada, si no se esta ejecutando iniciará la ejecución.

Se logueara la ejecución de este script en log/cron.log

#### loop
Script que ejecuta playbook de ansible recursivamente para recolectar información de los session border controller. Este esquema genérico de recolección pull puede aplicarse para otras situaciones.

![Figura 1](doc/sbctelemetry.png)
