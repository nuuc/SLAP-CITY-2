using UnityEngine;

public class CharacterBehaviour : MonoBehaviour
{
    public PolygonCollider2D ECBCollider;
    public Character character;
    private float acceleration;
    private Vector2 velocity = new Vector2(0, 0);
    private States states;
    private float gravity = -0.5f;
    private float terminalVelocity = -4;
    private float maxSpeed = 3;

    private void Start()
    {
        this.character = new ModelCharacter();
        this.states = new States(this, character);
    }

    private void Update()
    {
        
    }

    private void FixedUpdate()
    {
        PressedUpdate();
    }
    void PressedUpdate()
    {
        HandleInputs();
        HandleStates();
        MovementUpdate();
        Debug.Log(string.Format("Action State: {0} Frame: {1}", states.actionState, states.actionFrame));
        //Debug.Log(transform.position.y);

    }

    public void GroundCollision(Collider2D collider)
    {
        Vector2 velocity = GetVelocity();
        ColliderDistance2D cd = ECBCollider.Distance(collider);
        float distance = cd.distance;
        Vector2 translation = cd.normal * distance * 0.9f;
        Move(translation);
        // Should handle techs, special action states, etc.
        if (true)
        {

        }
        ChangeEnvState("grounded");
        ChangeActionState("lag", 2);
        Vector2 landingVelocity = new Vector2(velocity.x, 0);
        SetVelocity(landingVelocity);
    }

    public void Move(Vector2 translation)
    {
        Vector3 translation3 = translation;
        transform.Translate(translation3);
    }
    
    public void SetVelocity(Vector2 newVelocity)
    {
        velocity = newVelocity;
    }

    public Vector2 GetVelocity()
    {
        return velocity;
    }

    public void Accelerate(Vector2 acceleration)
    {
        velocity += acceleration;
    }

    private void HandleStates()
    {
        states.UpdateState();
        if (states.Airborne)
        {
            velocity.y += gravity;
            if (velocity.y < terminalVelocity)
            {
                velocity.y = terminalVelocity;
            }
        }
        else if (states.Grounded)
        {
            if (Mathf.Abs(velocity.x) > maxSpeed)
            {
                velocity.x = character.WalkMax * (velocity.x / Mathf.Abs(velocity.x));
            }
        }
    }

    private void HandleInputs()
    {
        Vector2 CStick = new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"));
        Debug.Log(Input.GetAxis("Horizontal"));

        if (states.Actionable)
        {
           if (states.Grounded)
            {
                if (Input.GetButton("Y"))
                {
                    states.StartJump();
                }
                else if (CStick.x != 0)
                {
                    int direction = (int) CStick.x;
                    states.StartWalk(direction);
                }
                else
                {
                    ChangeActionState("wait", 0);
                    Vector2 restVelocity = new Vector2(0, 0);
                    SetVelocity(restVelocity);
                }
            }
           else if (states.Airborne)
            {
                if (Input.GetButton("Y") & !states.dJumped)
                {
                    states.DoubleJump();
                }
            }
        }
        
    }

    private void MovementUpdate()
    {
        if (states.Airborne)
        {
            // Handle airborne movement
        }
        else if (states.Grounded)
        {
            // Handle grounded movement
        }
        Move(velocity);
    }

    public void ChangeActionState(string state, int frame = 0)
    {
        states.actionState = state;
        states.actionFrame = frame;
    }

    public void ChangeEnvState(string state)
    {
        states.envState = state;
    }

    public void Jump(bool SHop = false, int direction = 0)
    {
        Vector2 jumpVelocity = new Vector2(0, 0);
        float directionConstant = 0.1f;
        jumpVelocity.x = direction * directionConstant;
        if (!SHop)
        {
            jumpVelocity.y = character.FHopSpeed;
        }
        else
        {
            jumpVelocity.y = character.SHopSpeed;
        }
        SetVelocity(jumpVelocity);
    }
}

public class States
{

    private CharacterBehaviour characterBehaviour;
    private Character character;
    public string envState;
    public string actionState;
    public int actionFrame;
    public bool dJumped;
    public bool direction;
    public static int UNIVJUMPSQUAT = 2;

    public bool Grounded { get { return envState == "grounded"; } }

    public bool Airborne { get { return envState == "airborne"; } }

    public bool Actionable
    {
        get
        {
            return actionState == "wait" | actionState == "jump" | actionState == "djump" | actionState == "walk";
        }
    }

    public States(CharacterBehaviour characterBehaviour, Character character)
    {
        this.characterBehaviour = characterBehaviour;
        this.character = character;
        this.envState = "airborne";
        this.actionState = "jump";
        this.actionFrame = 0;
    }

    public void StartJump(int direction = 0)
    {
        // Direction will be encoded in actionState
        ChangeState("jumpsquat", 0);
    }

    public void DoubleJump(int direction = 0)
    {
        // Direction will be encoded in actionState

        ChangeState("djump", 0);
        characterBehaviour.Jump();
    }

    public void StartWalk(int direction)
    {
        ChangeState("walk", 0);
        Vector2 acceleration = new Vector2(character.WalkAcc * direction, 0);
        characterBehaviour.Accelerate(acceleration);
    }

    public void ChangeState(string action, int frame = 0)
    {
        actionState = action;
        actionFrame = frame;
    }

    public void UpdateState()
    {
        // Will also update character model in here
        switch (actionState)
        {
            case "lag":
                actionFrame--;
                if (actionFrame == 0)
                {
                    actionState = "wait";
                }
                break;

            case "jumpsquat":
                actionFrame++;
                if (actionFrame == UNIVJUMPSQUAT)
                {
                    envState = "airborne";
                    ChangeState("jump", 0);
                    characterBehaviour.Jump();
                }
                break;
            default:
                actionFrame = (actionFrame + 1) % 10;
                break;
        }
    }
}
