from .definition import ConsultDefinition
from .params import EcuParam

Definition = ConsultDefinition()


def params_to_command(params) -> bytes:
    cmd_bytes = bytes()
    for param in params:
        try:
            cmd_bytes += Definition.register_param
            cmd_bytes += param.get_registers()
        except Exception as e:
            print(f'Exception converting parameter {param.name} to command: {e}')
            raise e
    cmd_bytes += Definition.start_stream
    return cmd_bytes


def command_to_params(command) -> list[EcuParam]:
    params = []
    for i in range(0, len(command), 2):
        try:
            param = Definition.get_param(command[i:i+2])
            params.append(param)
        except Exception as e:
            print(f'Exception converting command to parameter: {e}')
            raise e
    return params