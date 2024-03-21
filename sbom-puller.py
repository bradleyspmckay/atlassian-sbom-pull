import docker
import argparse
import os

parser = argparse.ArgumentParser(prog='Atlassian-SBOM-Puller',
                                 description='This program will pull an Atlassian image and then extract its SBOM if one is available.',
                                 epilog='Please see https://github.com/bradleyspmckay/atlassian-sbom-pull for further documentation')

parser.add_argument('-i', '--image', dest='image', required=False, help='Full image path: registry.tld/repository/path/image:tag')
parser.add_argument('-il', '--image-list', dest='image_list', required=False, help='List of full paths to all images to be assessed')
parser.add_argument('-o', '--ouput', dest='output_directory', required=False, help='Name of output directory if not current directory')
#parser.add_argument()

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

def pull_and_run_image(images_to_assess):

    client = docker.from_env()

    for image in images_to_assess:

        # Pull the image, run it, and then extract the SBOM from it
        print(f'Pulling, running, and extracting SBOM from image: {image}')
        pulled_image = client.images.pull(image)
        container = client.containers.run(image, detach=True)
        exec_result = container.exec_run('sh -c "SBOM_LOCATION=$(find / -iname *sbom* 2>/dev/null); echo $SBOM_LOCATION"')
        print(exec_result.output.decode('utf-8'))

        # Kill and remove the container then remove the image
        container.kill()
        container.remove()
        client.containers.prune()
        pulled_image.remove()

if __name__ == "__main__":
    
    pull_and_run_image(images_to_assess)
