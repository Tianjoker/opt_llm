import argparse
import config
import logging
import os
import task


# Set up parser设置解析器
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str, default='config.json',
                    help='Federated learning configuration file.')
parser.add_argument('-l', '--log', type=str, default='INFO',
                    help='Log messages level.')

args = parser.parse_args()

# Set logging
logging.basicConfig(
    format='[%(levelname)s][%(asctime)s]: %(message)s', level=getattr(logging, args.log.upper()), datefmt='%H:%M:%S')


def main():
    """Run a federated learning simulation."""

    # Read configuration file
    opt_config = config.Config(args.config)

    # Initialize server初始化服务器
    opt_task = {
        "basic": task.Task(opt_config),
        # "random":task.RandomTask(opt_config),
        # "greedy": task.GreedyTask(opt_config),
        # "y-greedy": task.YGreedyTask(opt_config),
    }[opt_config.server.select]

    opt_task.boot()

    # Run federated learning
    opt_task.run()

if __name__ == "__main__":
    main()
