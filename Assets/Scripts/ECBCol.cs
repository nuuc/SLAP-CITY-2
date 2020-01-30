using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ECBCol : MonoBehaviour
{
    public CharacterBehaviour characterBehaviour;

    private void Start()
    {
        characterBehaviour = transform.GetComponentInParent<CharacterBehaviour>();
    }

    private void RegularCollide(Collision2D collision)
    {
        ColliderDistance2D cd = GetComponent<PolygonCollider2D>().Distance(collision.collider);
        float distance = cd.distance;
        Vector2 translation = cd.normal * distance;
        characterBehaviour.Move(translation);
    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.collider.CompareTag("Ground"))
        {
            characterBehaviour.GroundCollision(collision.collider);
        }
        else if (collision.collider.CompareTag("Edge"))
        {
            ColliderDistance2D cd = GetComponent<PolygonCollider2D>().Distance(collision.collider);
            float distance = cd.distance;
            Vector2 translation = cd.normal * distance;
            translation.y = 0;
            characterBehaviour.Move(translation);
        }
        else
        {
            RegularCollide(collision);
        }
    }

    private void OnCollisionStay2D(Collision2D collision)
    {
        if (collision.collider.CompareTag("Ground"))
        {
            ColliderDistance2D cd = GetComponent<PolygonCollider2D>().Distance(collision.collider);
            float distance = cd.distance;
            if (distance >= 0.15)
            {
                Debug.Log(distance);
                Vector2 translation = cd.normal * distance * 0.9f;
                characterBehaviour.Move(translation);
            }
            
        }
        else if (collision.collider.CompareTag("Edge"))
        {
            ColliderDistance2D cd = GetComponent<PolygonCollider2D>().Distance(collision.collider);
            float distance = cd.distance;
            Vector2 translation = cd.normal * distance;
            translation.y = 0;
            characterBehaviour.Move(translation);
        }
        else
        {
            RegularCollide(collision);
        }
    }

    private void OnCollisionExit2D(Collision2D collision)
    {
        if (collision.collider.CompareTag("Ground"))
        {
            characterBehaviour.ChangeEnvState("airborne");
            characterBehaviour.ChangeActionState("jump", 0);
        }
    }
}
