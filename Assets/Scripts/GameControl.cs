using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameControl : MonoBehaviour
{

    public int targetFPS = 60;
    // Start is called before the first frame update
    void Awake()
    {
        QualitySettings.vSyncCount = 0;
        Application.targetFrameRate = targetFPS;
    }

    // Update is called once per frame
    void Update()
    {
        if (Application.targetFrameRate != targetFPS)
            Application.targetFrameRate = targetFPS;
    }
}
