import docker
import argparse
import os

parser = argparse.ArgumentParser(prog='SBOM-Puller',
                                 description='This program will pull an Atlassian image and then extract its SBOM if one is available.')

def pull_and_run_image(registry, name, tag, command=None):
    client = docker.from_env()
    
    image = f"{registry}/{name}:{tag}"
    
    print(f"Pulling image: {image}")
    client.images.pull(image)
    
    print(f"Running container from image: {image}")
    container = client.containers.run(image, detach=True)
    
    if command:
        print(f"Executing command '{command}' within container {container.id}")
        exec_result = container.exec_run(command)
        print("Command output:")
        print(exec_result.output.decode('utf-8'))
    
    container.stop()
    container.remove()

if __name__ == "__main__":
    registry = input("Enter image registry (e.g., docker.io): ")
    name = input("Enter image name: ")
    tag = input("Enter image tag: ")
    command = input("Enter command to execute within the container (leave empty to skip): ")
    
    pull_and_run_image(registry, name, tag, command)
