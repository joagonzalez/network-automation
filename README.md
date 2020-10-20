# network-automation

![Python](https://img.shields.io/badge/automation-v1.0.0-orange)
![Python](https://img.shields.io/badge/ansible-v2.10.0-blue)
![Python](https://img.shields.io/badge/TextFSM-blue)
![Python](https://img.shields.io/badge/Jinja2-blue)
![Python](https://img.shields.io/badge/python-v3.8-blue)
![Python](https://img.shields.io/badge/platform-linux--64%7Cwin--64-lightgrey)

Repositorio con ejemplos de automatización orientados a infraestructura de telecomunicaciones. Puntualmente, dos ejemplos de telemetría y uno de automatización a través de workflow engine que utiliza inventario dinámico de ansible para aprovisionarse de los datos necesarios para ejecutarse.


## Telemetry ICMP

```bash
(network-automation) jgonzalez@turing:~/dev/network-automation/telemetry/ansible/sbc(master)$ ansible-playbook -i  hosts icmp.yml
```

## Telemetry SBC

```bash
(network-automation) jgonzalez@turing:~/dev/network-automation/telemetry/ansible/sbc(master)$ ansible-playbook -i inventory sbc.yml
```

## Automation SBC
Flujo para desarrollo

![automation](automation/doc/automation.png)

![automation_dag](automation/doc/dag.png)

Ver README.md de automation
