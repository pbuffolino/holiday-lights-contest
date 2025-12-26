import sys
import os
import argparse
import json
import signal
from lib.constants import NUM_PIXELS
from typing import Type
import importlib.util
from inspect import isclass

# Animation imports.
from lib.base_animation import BaseAnimation

# Controller imports.
from lib.matplotlib_controller import MatplotlibController


class AnimationRunner():
  def __init__(self, animation_class: Type[BaseAnimation], parameters: str, validate_parameters=True, background_color: str = 'gray') -> None:
    self.animation_class = animation_class
    kwargs = json.loads(parameters)

    self.c = MatplotlibController(self.animation_class, kwargs, NUM_PIXELS, validate_parameters=validate_parameters, background_color=background_color)

  def run(self):
    self.c.run()

  def stop(self):
    self.c.stop()


def load_animation_from_file(path: str) -> Type[BaseAnimation]:
  """Load an animation class from a Python file."""
  modname = os.path.splitext(os.path.basename(path))[0]
  spec = importlib.util.spec_from_file_location(modname, path)
  if spec is None:
    raise ValueError(f'Could not import {path}')
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  for attribute_name in dir(module):
    attribute = getattr(module, attribute_name)
    if isclass(attribute) and issubclass(attribute, BaseAnimation) and attribute is not BaseAnimation:            
      return attribute
  raise ValueError(f'No animation class found in {path}')


def list_samples():
  """List all available sample animations."""
  samples_dir = os.path.join(os.path.dirname(__file__), 'samples')
  if not os.path.exists(samples_dir):
    print("No samples directory found.")
    return
  
  samples = []
  for file_name in os.listdir(samples_dir):
    if file_name.endswith('.py') and file_name != '__init__.py':
      samples.append(os.path.splitext(file_name)[0])
  
  if samples:
    print("Available sample animations:")
    for sample in sorted(samples):
      print(f"  - {sample}")
  else:
    print("No sample animations found.")


def get_sample_path(sample_name: str) -> str:
  """Get the path to a sample animation file."""
  samples_dir = os.path.join(os.path.dirname(__file__), 'samples')
  sample_path = os.path.join(samples_dir, f"{sample_name}.py")
  
  if not os.path.exists(sample_path):
    print(f"Error: Sample '{sample_name}' not found.")
    print("Use --list-samples to see available samples.")
    sys.exit(1)
  
  return sample_path


if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog="run_animation", 
                                   description="Script for running animations with matplotlib visualization")
  parser.add_argument('--args', 
                      help='JSON string with custom arguments for the animation',
                      type=str, 
                      default="{}")
  parser.add_argument('--no_validation',
                      help='skip validating the supplied args list against the animation',
                      action='store_true')
  parser.add_argument('--sample',
                      help='run a sample animation directly from the samples folder',
                      type=str)
  parser.add_argument('--list-samples',
                      help='list all available sample animations',
                      action='store_true')
  parser.add_argument('--background',
                      help='background color for the matplotlib visualization (default: gray)',
                      type=str,
                      default='gray')
  args = parser.parse_args()

  # Handle list-samples
  if args.list_samples:
    list_samples()
    exit(0)
  
  # Determine which animation file to load
  if args.sample:
    animation_path = get_sample_path(args.sample)
  else:
    animation_path = os.path.join(os.path.dirname(__file__), 'animation.py')
    if not os.path.exists(animation_path):
      print(f"Error: animation.py not found.")
      print("Create an animation.py file with your animation class, or use --sample <name> to run a sample.")
      sys.exit(1)

  try:
    animation_class = load_animation_from_file(animation_path)
    ar = AnimationRunner(animation_class, args.args, validate_parameters=not args.no_validation, background_color=args.background)
  except Exception as e:
    print(f"Error loading animation: {e}")
    sys.exit(1)

  def _handle_sigterm(*args):
    ar.stop()

  def _handle_sigint(*args):
    ar.stop()

  signal.signal(signal.SIGTERM, _handle_sigterm)
  signal.signal(signal.SIGINT, _handle_sigint)
  ar.run()

