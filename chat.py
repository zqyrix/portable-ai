from brain import Brain

brain = Brain()
print("\n" + "="*40)
print("  ZQYRIX — Text Mode")
print("="*40)
print("  Type 'bye' to exit\n")

while True:
    user = input("You: ").strip()
    if not user: continue
    if user.lower() in ["bye","exit","quit"]:
        print("Zqyrix: Catch you later Nithin!")
        break
    reply = brain.think(user)
    print(f"\nZqyrix: {reply}\n")