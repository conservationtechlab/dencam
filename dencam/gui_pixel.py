"""Classes for different gui pixel values

Fenrir needs BusterConfig gui pixel values, and
Lesehest and Mimir need BookwormConfig pixel values.

"""
class BusterConfig:
    """Pixel values for Buster OS

    """
    values = {
        "recorder_vid_count_label": [40, 130],
        "recorder_device_label": [40, 170],
        "recorder_storage_label": [40, 210],
        "recorder_time_label": [40, 250],
        "recorder_error_label": [100, 200, 0, 430],
        "recorder_next_page": [50, 160, 0, 364],
        "recorder_toggle_recording": [50, 270, 0, 240],
        "network_ip_label": [0, 50],
        "network_version_label": [70, 490, 380],
        "network_next_page": [50, 160, 0, 364],
        "network_airplane_mode": [50, 220, 0, 240],
        "blank_next_page": [50, 160, 0, 364],
        "blank_toggle": [50, 440, 0, 430],
        "solar_solar_label": [0, 50],
        "solar_next_page": [50, 160, 0, 364],
        "solar_update_data": [50, 190, 0, 240],
    }


class BookwormConfig:
    """Pixel values for Bookworm OS

    """
    values = {
        "recorder_vid_count_label": [20, 65],
        "recorder_device_label": [20, 85],
        "recorder_storage_label": [20, 105],
        "recorder_time_label": [20, 125],
        "recorder_error_label": [100, 200, 0, 430],
        "recorder_next_page": [25, 80, 0, 182],
        "recorder_toggle_recording": [25, 135, 0, 120],
        "network_version_label": [70, 245, 170],
        "network_next_page": [25, 80, 0, 182],
        "network_airplane_mode": [25, 110, 0, 120],
        "blank_next_page": [50, 145, 495, 430],
        "blank_toggle": [50, 440, 0, 430],
        "solar_solar_label": [0],
        "solar_next_page": [25, 80, 0, 182],
        "solar_update_data": [25, 95, 0, 120],
    }
