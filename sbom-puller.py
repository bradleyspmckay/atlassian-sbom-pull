import docker
import argparse
import os

parser = argparse.ArgumentParser(prog='Atlassian-SBOM-Puller',
                                 description='This program will pull an Atlassian image and then extract its SBOM if one is available.',
                                 epilog='Please see https://github.com/bradleyspmckay/atlassian-sbom-pull for further documentation')

parser.add_argument('-i', '--image', dest='image', required=False, help='Full image path: registry.tld/repository/path/image:tag')
parser.add_argument('-il', '--image-list', dest='image_list', required=False, help='List of full paths to all images to be assessed')
parser.add_argument('-od', '--ouput-directory', dest='output_directory', required=False, help='Name of output directory if not current directory')

args = parser.parse_args()

# Check if image path or list of image paths was provided and exit if not
if not args.image and not args.image_list:
    print('Please provide an image path or file containing a list of image paths')
    exit()

images_to_assess = []

if args.image:
    images_to_assess.append(args.image)

if args.image_list:
    with open(args.image_list, 'r') as file:
        for line in file:
            images_to_assess.append(line)

if images_to_assess == []:
    print('Failed to prime image or list of images, please check your input to -i or -il')
    exit()

def pull_and_run_image(images_to_assess, output_directory):

    client = docker.from_env()

    for image in images_to_assess:

        # Create output directory for this image
        directory_to_store_sboms = f'{output_directory}/{image}'
        os.makedirs(directory_to_store_sboms)

        # Pull the image and run it
        print(f'Working on {image}')
        pulled_image = client.images.pull(image)
        container = client.containers.run(image, detach=True)

        # The sh commands to run inside the container to extract SBOM
        command =  'sh -c "find / -iname *sbom*.json 2>/dev/null"'

        # Run the command and catch the resulting bytes and error
        error, exec_result = container.exec_run(command)
        if error != 0:
            print(f'Shell command ran within {image} exited with code {error}. Moving on ...')
        else:
            # Create output directory for this image if it does not already exist
            directory_to_store_sboms = f'{output_directory}/{image}'
            if not os.path.isdir(directory_to_store_sboms):
                os.makedirs(directory_to_store_sboms)

            sboms_to_extract = exec_result.decode("utf-8").split()

            for sbom in sboms_to_extract:
                tar_stream = container.get_archive(sbom)
                with open(f'{directory_to_store_sboms}/{sbom}', 'wb') as output_sbom_file:
                    output_sbom_file.write(tar_stream)

        # Kill/remove the container and remove the image
        container.kill()
        container.remove()
        client.containers.prune()
        pulled_image.remove()

if __name__ == "__main__":
    
    if args.output_directory != None:
        pull_and_run_image(images_to_assess, args.output_directory)
    else:
        pull_and_run_image(images_to_assess, os.getcwd())
