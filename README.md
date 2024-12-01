# SD5913GroupAssignment
This is the group assignment from HUO Junjie, SUN Ming and CHEN Qiyue!

BallShift is an interesting eat ball game written in python using the pygame library. Here are some instructions:

## Environment Requirements

- Python Version: 3.10 or higher
- Dependencies: See 'requirements.txt'

## Installation and Running the Game

1. Ensure that Python 3.10 or higher is installed on your system.
2. Clone or download the project code to your local machine.
3. Make sure you are in the folder which named 'SD5913GroupAssignment' and run the following command to install the required dependencies:

   ```bash
   pip install -r requirements.txt
4. After installing all dependencies, you can run the game with the following command:

    ```bash
    python main.py

## Player Control Instruction

1. Use the arrow keys (↑ ↓ ← →) to control the movement of your ball.
2. Press the Shift key to release a skill. (There are three skills in the game)
  - Speedup: 50% speed increase in 10 seconds.
  - Flash: Flashes a distance in the current direction of movement.
  - Invincible: Gain 10 seconds of invincibility.

## Game Rules

1. There will be one player and three enemies in a game.
2. Big ball can eat smaller balls, and the big ball will get bigger after eating other balls.
3. As the ball gets bigger, its movement speed will decrease.
4. A batch of Fruit Balls and Skill Balls will be refreshed in the scene at regular intervals, with a maximum of 20 Fruit Balls and 3 Skill Balls existing in the scene after each refresh.
  - Both the player and enemies can get bigger by eating fruit balls.
  - Both the player and enemies can gain skills by eating skill balls.
5. The game ends when the player reaches the victory condition or the defeat condition.
  - Victory condition: the player's ball eats all enemies.
  - Defeat condition: the player's ball is eaten by the enemies.

Now it's your time to have fun in this game!!! If you have any questions, feel free to contact us via 24073512g@connect.polyu.hk!