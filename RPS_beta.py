import cv2
import mediapipe as mp
import math
import time
import random

# Initialize game variables
l = ["Rock", "Paper", "Scissor"]
R = cv2.imread("Rock.png", 1)
P = cv2.imread("Paper.png", 1)
S = cv2.imread("Scissor.jpg", 1)

R = cv2.resize(R, (400, 400))
P = cv2.resize(P, (400, 400))
S = cv2.resize(S, (400, 400))

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
pTime = 0
cTime = 0

wcam = 720
hcam = 640

UserName = input("Enter your name: ")
Score_User = 0  # Initialize user's score
Score_Comp = 0  # Initialize computer's score

def main():
    print("Welcome to Rock Paper Scissors by Priyanshu")
    response = int(input("Press 1 for the rules or 2 to continue to the game : "))
    if response == 1:
        Rules()
    elif response == 2:
        Game_processing()
    else:
        print("Invalid button, try again")
        main()

def Rules():
    rules = [
        "Enter '-' to read next rule",
        "Have a bit of patience, as Camera is little lazy",
        "In the game zone when the camera opens, start by showing your hand symbol around 30 cm(allowed range) from the camera.",
        "Move your hand a little back and forth slowly by being in the allowed range.",
        "After sometime your response will be captured and compared with the computer's choice and winner will be declared accordingly",
        "Only standard symbols are allowed and within the range only and avoid putting random hand in the camera view which may confuse it and it can scan that by mistake and results can be declared.",
        "There will be 5 rounds in total, at the end of which we will get a winner, loser, or a draw.",
        "To quit the game in between, press q when the camera is open",
        "Are you ready?"
    ]
    for rule in rules:
        print(rule)
        response2 = input()
        if response2 == "-" :
            continue
        else:
            break
    Game_processing()


def Computer_Game():
    comp_turn = random.choice(l)
    if comp_turn == "Rock":
        cv2.imshow('Computer Choice', R)
    elif comp_turn == "Paper":
        cv2.imshow('Computer Choice', P)
    else:
        cv2.imshow('Computer Choice', S)
    return comp_turn

def User_Game(middleTip_base, ringPip_thumbTip):
    if 50 < middleTip_base < 160 and 50 < ringPip_thumbTip < 160:
        return "Rock"
    elif middleTip_base > 350 and ringPip_thumbTip > 250:
        return "Paper"
    elif middleTip_base > 350 and ringPip_thumbTip < 30:
        return "Scissor"
    else:
        return None

def Game_processing():
    global playzone, playzoneRGB, user_turn, comp_turn, Score_User, Score_Comp
    cap = cv2.VideoCapture(0)
    cap.set(3, wcam)
    cap.set(4, hcam)
    rounds = 5

    while rounds > 0:
        ret, playzone = cap.read()
        playzoneRGB = cv2.cvtColor(playzone, cv2.COLOR_BGR2RGB)
        results = hands.process(playzoneRGB)
        Lmlist = []
        show_fps(playzone)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, d = playzoneRGB.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    Lmlist.append([id, cx, cy])
                mpDraw.draw_landmarks(playzoneRGB, handLms, mpHands.HAND_CONNECTIONS)

                if Lmlist:
                    x1, y1 = Lmlist[0][1], Lmlist[0][2]
                    x2, y2 = Lmlist[12][1], Lmlist[12][2]
                    x3, y3 = Lmlist[4][1], Lmlist[4][2]
                    x4, y4 = Lmlist[14][1], Lmlist[14][2]

                    #draw_points_and_lines(playzoneRGB, x1, y1, x2, y2, x3, y3, x4, y4)

                    middleTip_base = math.hypot(x2 - x1, y2 - y1)
                    ringPip_thumbTip = math.hypot(x4 - x3, y4 - y3)

                    user_turn = User_Game(middleTip_base, ringPip_thumbTip)

                    if user_turn:
                        cap.release()
                        cv2.destroyAllWindows()

                        comp_turn = Computer_Game()
                        cv2.waitKey(4000)
                        cv2.destroyAllWindows()

                        display_winner(user_turn, comp_turn)
                        cv2.waitKey(4000)
                        cv2.destroyAllWindows()

                        rounds -= 1
                        cap = cv2.VideoCapture(0)
                        cap.set(3, wcam)
                        cap.set(4, hcam)

        playzone = cv2.cvtColor(playzoneRGB, cv2.COLOR_RGB2BGR)
        cv2.imshow('Play Zone', playzone)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Game Over")
    print(f"{UserName}'s Score: {Score_User}")
    print(f"Computer's Score: {Score_Comp}")

#def draw_points_and_lines(playzoneRGB, x1, y1, x2, y2, x3, y3, x4, y4):
#    cv2.circle(playzoneRGB, (x1, y1), 7, (0, 255, 255), cv2.FILLED)
#    cv2.circle(playzoneRGB, (x2, y2), 7, (0, 255, 255), cv2.FILLED)
#    cv2.circle(playzoneRGB, (x3, y3), 7, (0, 255, 255), cv2.FILLED)
#    cv2.circle(playzoneRGB, (x4, y4), 7, (0, 255, 255), cv2.FILLED)
#    cv2.line(playzoneRGB, (x1, y1), (x2, y2), (235, 206, 135), 2)
#    cv2.line(playzoneRGB, (x3, y3), (x4, y4), (235, 206, 135), 2)

def show_fps(playzone):
    global pTime, cTime
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(playzone, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

def display_winner(user_turn, comp_turn):
    global Score_User, Score_Comp
    if user_turn == comp_turn:
        text = "It's a Tie"
    elif (user_turn == "Rock" and comp_turn == "Scissor") or \
            (user_turn == "Scissor" and comp_turn == "Paper") or \
            (user_turn == "Paper" and comp_turn == "Rock"):
        text = "You Win!"
        Score_User += 1
    else:
        text = "You Lose!"
        Score_Comp += 1
    cv2.putText(playzone, text, (50, 250), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255), 3)

    cv2.imshow('Play Zone', playzone)

if __name__ == "__main__":
    main()
