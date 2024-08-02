from .definition import ConsultDefinition, ParamID
from .params import EcuParam

Definition = ConsultDefinition()


def param_ids_to_param(param_ids: iter(ParamID)) -> list[EcuParam]:
    params = []
    for param_id in param_ids:
        try:
            param = Definition.get_parameter(param_id)
            params.append(param)
        except Exception as e:
            print(f'Exception converting parameter ID {param_id} to parameter: {e}')
            raise e
    return params


def params_to_command(param_ids) -> bytes:
    cmd_bytes = bytearray()
    for param in param_ids_to_param(param_ids):
        try:
            cmd_bytes.append(Definition.register_param)
            cmd_bytes.append(param.get_register())
        except Exception as e:
            print(f'Exception converting parameter {param.name} to command: {e}')
            raise e
    cmd_bytes.append(Definition.start_stream)
    return cmd_bytes


def command_to_params(command: bytes) -> list[EcuParam]:
    params = []
    for i in range(0, len(command)):
        if command[i] == Definition.register_param:
            continue
        if command[i] == Definition.start_stream:
            break
        try:
            cmd_byte = command[i]
            param = Definition.get_parameter_from_register(command[i])
            params.append(param)
        except Exception as e:
            print(f'Exception converting command byte {command[i]} to parameter: {e}')
            raise e
    return params
