using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public abstract class Character
{
    public float Gravity { get; set; }
    public float Friction { get; set; }
    public float AirFriction { get; set; }
    public float[] AirSpeedMax { get; set; }
    public float DashAcc { get; set; }
    public float DashMax { get; set; }
    public float WalkAcc { get; set; }
    public float WalkMax { get; set; }
    public float FHopSpeed { get; set; }
    public float SHopSpeed { get; set; }
    public float Weight { get; set; }
    public float HighTractionSpeed { get; set; }
    // Some attribute for character model

}

public class ModelCharacter : Character
{
    public ModelCharacter()
    {
        this.Gravity = -1.18f;
        this.Friction = 0.24f;
        this.WalkAcc = 0.5f;
        this.WalkMax = 5f;
        this.FHopSpeed = 18.84f;
        this.SHopSpeed = 10.41f;
    }
}
