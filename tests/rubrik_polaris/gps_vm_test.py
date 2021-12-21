import os

import pytest

from conftest import util_load_json, BASE_URL
from rubrik_polaris.common import validations
from rubrik_polaris.gps.vm import ERROR_MESSAGES


def test_create_vm_snapshot_when_valid_values_are_provided(requests_mock, client):
    """
    Tests create_vm_snapshot method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.vm import create_vm_snapshot

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/gps_vm_snapshot_create_response.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = create_vm_snapshot(client, snapshot_id="dummy_id", sla_id=None)
    assert response == expected_response


@pytest.mark.parametrize("snapshot_id, sla_id, err_msg", [
    ("", "", validations.ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('snapshot_id'))
])
def test_create_vm_snapshot_when_invalid_values_are_provided(client, snapshot_id, sla_id, err_msg):
    """
    Tests create_vm_snapshot method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.gps.vm import create_vm_snapshot

    with pytest.raises(ValueError) as e:
        create_vm_snapshot(client, snapshot_id=snapshot_id, sla_id=sla_id)
    assert str(e.value) == err_msg


def test_create_vm_livemount_when_valid_values_are_provided(requests_mock, client):
    """
    Tests create_vm_livemount method of PolarisClient by passing valid inputs
    """

    from rubrik_polaris.gps.vm import create_vm_livemount

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/create_vm_livemount.json"))

    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = create_vm_livemount(client, snapshot_fid="1234")

    assert response == expected_response


@pytest.mark.parametrize(
    "snapshot_fid, host_id, vm_name, disable_network, remove_network_devices, power_on, keep_mac_addresses,"
    "data_store_name, "
    "create_data_store_only, vlan, should_recover_tags, err_msg",
    [
        ("", None, None, None, None, None, None, None, None, None, None,
         validations.ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("snapshot_fid")),
        ("1234", None, None, "abc", None, None, None, None, None, None, None,
         validations.ERROR_MESSAGES['INVALID_BOOLEAN']),
        ("1234", None, None, None, "abc", None, None, None, None, None, None,
         validations.ERROR_MESSAGES['INVALID_BOOLEAN']),
    ])
def test_create_vm_livemount_when_invalid_values_are_provided(client, snapshot_fid, host_id, vm_name, disable_network,
                                                              remove_network_devices, power_on, keep_mac_addresses,
                                                              data_store_name, create_data_store_only, vlan,
                                                              should_recover_tags, err_msg):
    """
    Tests create_vm_livemount method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.gps.vm import create_vm_livemount

    with pytest.raises(ValueError) as e:
        create_vm_livemount(client, snapshot_fid=snapshot_fid, host_id=host_id, vm_name=vm_name,
                            disable_network=disable_network,
                            remove_network_devices=remove_network_devices, power_on=power_on,
                            keep_mac_addresses=keep_mac_addresses,
                            data_store_name=data_store_name, create_data_store_only=create_data_store_only, vlan=vlan,
                            should_recover_tags=should_recover_tags)

    assert str(e.value) == err_msg


def test_list_vsphere_hosts_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_vsphere_hosts method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.vm import list_vsphere_hosts

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/list_vsphere_hosts.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = list_vsphere_hosts(client, first=1000)
    assert response == expected_response


@pytest.mark.parametrize("first, after, filters, sort_by,sort_order, err_msg", [
    (None, None, None, None, None, ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("first")),
    (-10, None, None, None, None, validations.ERROR_MESSAGES['INVALID_FIRST'].format(-10)),
    ("x", None, None, None, None, validations.ERROR_MESSAGES['INVALID_NUMBER'].format("x")),
    (10, None, None, "NAME", "BOTH",
     ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("BOTH", "sort_order", ['ASC', 'DESC']))
])
def test_list_vsphere_hosts_when_invalid_values_are_provided(client, requests_mock, after, first, filters, sort_by,
                                                             sort_order, err_msg):
    """
    Tests list_vsphere_hosts of PolarisClient when invalid values are provided.
    """
    from rubrik_polaris.gps.vm import list_vsphere_hosts

    enum_sort_by = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_by_values.json")
    )
    enum_sort_order = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
    )
    responses = [
        {'json': enum_sort_by},
        {'json': enum_sort_order},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_vsphere_hosts(client, after=after, first=first, filters=filters, sort_by=sort_by, sort_order=sort_order)

    assert str(e.value) == err_msg


def test_export_vm_snapshot_when_valid_values_are_provided(requests_mock, client):
    """
    Tests export_vm_snapshot method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.vm import export_vm_snapshot

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/export_vm_snapshot.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    config = {
        "datastoreId": "711f8a94-c7dd-5ea9-afe9-2d8e44d09d3d",
        "requiredRecoveryParameters": {"snapshotId": "e9e1980f-11f0-53f3-84d6-15f60264b63b"},
        "hostId": "f57bfebf-c7c9-5310-a5fd-1f0aeea5ba25"
    }
    response = export_vm_snapshot(client, id_="dc4f1b47-da71-5a62-a4eb-b94406d74cbc", config=config)
    assert response == expected_response


@pytest.mark.parametrize("id_, config, err_msg", [
    (None, None, validations.ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("id_")),
    ("dc4f1b47-da71-5a62-a4eb-b94406d74cbc", None, ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('config')),
    ("dc4f1b47-da71-5a62-a4eb-b94406d74cbc", "x", ERROR_MESSAGES['INVALID_CONFIG'].format("x")),
    ("dc4f1b47-da71-5a62-a4eb-b94406d74cbc", {"dummy_key": "dummy_value"},
     ERROR_MESSAGES['REQUIRED_KEYS_IN_CONFIG'])
])
def test_export_vm_snapshot_when_invalid_values_are_provided(client, id_, config, err_msg):
    """
    Tests export_vm_snapshot of PolarisClient when invalid values are provided.
    """
    from rubrik_polaris.gps.vm import export_vm_snapshot

    with pytest.raises(ValueError) as e:
        export_vm_snapshot(client, id_=id_, config=config)

    assert str(e.value) == err_msg


def test_list_vsphere_datastores_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_vsphere_datastores method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.vm import list_vsphere_datastores

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/list_vsphere_datastores.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = list_vsphere_datastores(client, host_id="dummy", first=2)
    assert response == expected_response


@pytest.mark.parametrize("host_id, first, after, filters, sort_by,sort_order, err_msg", [
    (None, None, None, None, None, None, ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("host_id")),
    ("dummy", -10, None, None, None, None, validations.ERROR_MESSAGES['INVALID_FIRST'].format(-10)),
    ("dummy", "x", None, None, None, None, validations.ERROR_MESSAGES['INVALID_NUMBER'].format("x")),
    ("dummy", None, None, None, "NAME", "BOTH",
     ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("BOTH", "sort_order", ['ASC', 'DESC']))
])
def test_list_vsphere_datastores_when_invalid_values_are_provided(client, requests_mock, host_id, first, after,
                                                                  filters, sort_by, sort_order, err_msg):
    """
    Tests list_vsphere_datastores of PolarisClient when invalid values are provided.
    """
    from rubrik_polaris.gps.vm import list_vsphere_datastores

    enum_sort_by = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/hierarchy_sort_by_values.json")
    )
    enum_sort_order = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
    )
    responses = [
        {'json': enum_sort_by},
        {'json': enum_sort_order},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_vsphere_datastores(client, host_id=host_id, after=after, first=first, filters=filters, sort_by=sort_by,
                                sort_order=sort_order)

    assert str(e.value) == err_msg


def test_get_async_request_result_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_async_request_result method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.vm import get_async_request_result

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/gps_get_async_request_result_response.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_async_request_result(client, "dummy-request-id", "dummy-cluster-id")
    assert response == expected_response


@pytest.mark.parametrize("request_id, cluster_id, err_msg", [
    ("", "dummy-cluster-id", ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('request_id')),
    ("dummy-request-id", "", ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('cluster_id'))
])
def test_get_async_request_result_when_invalid_values_are_provided(client, request_id, cluster_id, err_msg):
    """
    Tests get_async_request_result method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.gps.vm import get_async_request_result

    with pytest.raises(ValueError) as e:
        get_async_request_result(client, request_id=request_id, cluster_id=cluster_id)
    assert str(e.value) == err_msg


@pytest.mark.parametrize("snapshot_id, cluster_id, restore_config, err_msg", [
    ("", "", {
        "path": "/var/empty",
        "restorePath": "/usr/share"
    }, ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("snapshot_id")),
    (" 123 ", "", {
        "path": "/var/empty",
        "restorePath": "/usr/share"
    }, validations.ERROR_MESSAGES['INVALID_ID_FORMAT'].format(" 123 ", "snapshot_id")),
    ("dummy-snapshot-id", "", {
        "path": "/var/empty",
        "restorePath": "/usr/share"
    }, ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("cluster_id")),
    ("dummy-snapshot-id", " 123 ", {
        "path": "/var/empty",
        "restorePath": "/usr/share"
    }, validations.ERROR_MESSAGES['INVALID_ID_FORMAT'].format(" 123 ", "cluster_id")),
    ("dummy-snapshot-id", "dummy-cluster-id", {}, ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("restore_config")),
    ("dummy-snapshot-id", "dummy-cluster-id", [], ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("restore_config"))
])
def test_recover_files_when_invalid_values_are_provided(client, snapshot_id, cluster_id, restore_config, err_msg):
    """
    Tests recover_files method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.gps.vm import recover_files

    with pytest.raises(ValueError) as e:
        recover_files(client, snapshot_id, cluster_id, {})
    assert str(e.value) == err_msg


def test_recover_files_when_valid_values_are_provided(requests_mock, client):
    """
    Tests recover_files method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.vm import recover_files

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/gps_recover_files_response.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = recover_files(client, "dummy-request-id", "dummy-cluster-id", [{
        "path": "/var/empty",
        "restorePath": "/usr/share"
    }])
    assert response == expected_response
