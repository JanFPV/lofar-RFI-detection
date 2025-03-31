from lofarimaging import read_acm_cube, make_xst_plots
from lofarimaging.rfi_tools import generate_movie_from_list

__all__ = [
    "generate_time_sweep",
    "generate_subband_sweep",
    "generate_height_sweep",
]

def generate_time_sweep(df, subbands, height, station_name, station_type, rcu_mode, temp_dir, output_dir, fps=10):
    """
    Generate a time sweep movie from the given DataFrame and parameters.
    Args:
        df (pd.DataFrame): DataFrame containing the data files and their metadata.
        subbands (list): List of subbands to process.
        height (float): Height for the plots.
        station_name (str): Name of the station.
        station_type (str): Type of the station.
        rcu_mode (str): RCU mode.
        temp_dir (str): Temporary directory for storing images.
        output_dir (str): Output directory for the movie.
        fps (int): Frames per second for the movie.
    """

    print("Generating images for time sweep...")

    sky_movie = []
    nf_movie = []

    # Loop to generate images for each subband and time
    for subband in subbands:
        subband_data = df[df['subband'] == subband].head(3)

        for index, row in subband_data.iterrows():
            xst_filename = row['dat_file']
            obstime = row['timestamp']

            try:
                print(f"Generating image for subband {subband} at time {obstime} and heigth {height} m.")
                visibilities = read_acm_cube(xst_filename, station_type)[0]
                sky_image_path, nf_image_path, _ = make_xst_plots(visibilities, station_name, obstime, subband, rcu_mode, map_zoom=18, outputpath=temp_dir, mark_max_power=True, height=height, return_only_paths=True)
                sky_movie.append(sky_image_path)
                nf_movie.append(nf_image_path)
            except Exception as e:
                print(f"Error generating image for {xst_filename}: {e}")

    # Export the image lists for movie generation
    with open(f"{temp_dir}/sky_image_list_time_sweep.txt", "w") as sky_file:
        sky_file.write("\n".join(sky_movie))

    with open(f"{temp_dir}/nf_image_list_time_sweep.txt", "w") as nf_file:
        nf_file.write("\n".join(nf_movie))

    print("Image generation complete for time sweep.")
    generate_movie_from_list(f"{temp_dir}/sky_image_list_time_sweep.txt", f"{output_dir}/sky_movie_time_sweep.mp4", fps=fps)
    generate_movie_from_list(f"{temp_dir}/nf_image_list_time_sweep.txt", f"{output_dir}/nf_movie_time_sweep.mp4", fps=fps)
    print("Movie generation complete.")
    return


def generate_subband_sweep(df, times, subbands, height, station_name, station_type, rcu_mode, temp_dir, output_dir, fps=10):
    '''
    Generate a subband sweep movie from the given DataFrame and parameters.
    Args:
        df (pd.DataFrame): DataFrame containing the data files and their metadata.
        times (list): List of times to process.
        subbands (list): List of subbands to process.
        height (float): Height for the plots.
        station_name (str): Name of the station.
        station_type (str): Type of the station.
        rcu_mode (str): RCU mode.
        temp_dir (str): Temporary directory for storing images.
        output_dir (str): Output directory for the movie.
        fps (int): Frames per second for the movie.
    '''

    print("Generating images for subband sweep...")

    sky_movie = []
    nf_movie = []

    # Loop to generate images for each subband and time
    for t in times:
        for subband in subbands:
            subband_data = df[df['subband'] == subband]

            subband_data = subband_data[subband_data['timestamp'] >= t]
            subband_data = subband_data.sort_values('timestamp')
            closest_row = subband_data.iloc[0] if not subband_data.empty else None

            if closest_row is None:
                print(f"No data found for subband {subband} at {t}")
                continue

            xst_filename = closest_row['dat_file']
            obstime = closest_row['timestamp']

            try:
                print(f"Generating image for subband {subband} at time {obstime} and heigth {height} m.")
                visibilities = read_acm_cube(xst_filename, station_type)[0]
                sky_image_path, nf_image_path, _ = make_xst_plots(visibilities, station_name, obstime, subband, rcu_mode, map_zoom=18, outputpath=temp_dir, mark_max_power=True, height=height, return_only_paths=True)
                sky_movie.append(sky_image_path)
                nf_movie.append(nf_image_path)
            except Exception as e:
                print(f"Error generating image for {xst_filename}: {e}")

    # Export the image lists for movie generation
    with open(f"{temp_dir}/sky_image_list_subband_sweep.txt", "w") as sky_file:
        sky_file.write("\n".join(sky_movie))

    with open(f"{temp_dir}/nf_image_list_subband_sweep.txt", "w") as nf_file:
        nf_file.write("\n".join(nf_movie))

    print("Image generation complete for subband sweep.")
    generate_movie_from_list(f"{temp_dir}/sky_image_list_subband_sweep.txt", f"{output_dir}/sky_movie_subband_sweep.mp4", fps=fps)
    generate_movie_from_list(f"{temp_dir}/nf_image_list_subband_sweep.txt", f"{output_dir}/nf_movie_subband_sweep.mp4", fps=fps)
    print("Movie generation complete.")
    return


def generate_height_sweep(df, times, subbands, heights, station_name, station_type, rcu_mode, temp_dir, output_dir, fps=10):
    '''
    Generate a height sweep movie from the given DataFrame and parameters.
    Args:
        df (pd.DataFrame): DataFrame containing the data files and their metadata.
        times (list): List of times to process.
        subbands (list): List of subbands to process.
        heights (list): List of heights to process.
        station_name (str): Name of the station.
        station_type (str): Type of the station.
        rcu_mode (str): RCU mode.
        temp_dir (str): Temporary directory for storing images.
        output_dir (str): Output directory for the movie.
        fps (int): Frames per second for the movie.
    '''

    print("Generating images for height sweep...")

    sky_movie = []
    nf_movie = []

    # Loop to generate images for each subband and time
    for t in times:
        for subband in subbands:
            subband_data = df[df['subband'] == subband]

            subband_data = subband_data[subband_data['timestamp'] >= t]
            subband_data = subband_data.sort_values('timestamp')
            closest_row = subband_data.iloc[0] if not subband_data.empty else None

            if closest_row is None:
                print(f"No data found for subband {subband} at {t}")
                continue

            for height in heights:
                xst_filename = closest_row['dat_file']
                obstime = closest_row['timestamp']

                try:
                    print(f"Generating image for subband {subband} at time {obstime} and heigth {height} m.")
                    visibilities = read_acm_cube(xst_filename, station_type)[0]
                    sky_image_path, nf_image_path, _ = make_xst_plots(visibilities, station_name, obstime, subband, rcu_mode, map_zoom=18, outputpath=temp_dir, mark_max_power=True, height=height, return_only_paths=True)
                    sky_movie.append(sky_image_path)
                    nf_movie.append(nf_image_path)
                except Exception as e:
                    print(f"Error generating image for {xst_filename}: {e}")

    # Export the image list for movie generation
    with open(f"{temp_dir}/nf_image_list_heigth_sweep.txt", "w") as nf_file:
        nf_file.write("\n".join(nf_movie))

    print("Image generation complete for height sweep.")
    generate_movie_from_list(f"{temp_dir}/nf_image_list_heigth_sweep.txt", f"{output_dir}/nf_movie_heigth_sweep.mp4", fps=fps)
    print("Movie generation complete.")
    return
