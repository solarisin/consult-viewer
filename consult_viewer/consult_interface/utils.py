from .definition import ConsultDefinition, ParamID
from .params import EcuParam

Definition = ConsultDefinition()


def param_ids_to_param(param_ids: iter(ParamID)) -> list[EcuParam]:
    params = []
    for param_id in param_ids:
        try:
            param = Definition.parameters[param_id]
            params.append(param)
        except Exception as e:
            print(f'Exception converting parameter ID {param_id} to parameter: {e}')
            raise e
    return params


def params_to_command(param_ids) -> bytes:
    cmd_bytes = bytes()
    for param in param_ids_to_param(param_ids):
        try:
            cmd_bytes += Definition.register_param
            cmd_bytes += param.get_register()
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