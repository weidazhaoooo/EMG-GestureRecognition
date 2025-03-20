using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class ZmqSubscriberExample : MonoBehaviour {

    public static ZmqSubscriberExample Instance;

    ZmqCommunicator zmqSub;
    
    // The IP address should match the one set in Python
    public string ip = "tcp://127.0.0.1:5000"; 

    public float updateInterval = 0.01f;   // Check for messages every 10ms

    // Event that other components can subscribe to
    public delegate void GestureReceivedHandler(string gesture);
    public event GestureReceivedHandler OnGestureReceived;

    void Awake() {
        if (Instance == null) {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else if (Instance != this) {
            Destroy(gameObject);
            return;
        }               

        zmqSub = gameObject.AddComponent<ZmqCommunicator>();
    }

    private void OnEnable() {
        zmqSub.StartSubscriber(ip, updateInterval, ReadMessage);
        Debug.Log("ZMQ Subscriber started, listening for EMG classifications at " + ip);
    }

    private void OnDisable() {
        zmqSub.Stop();
        Debug.Log("ZMQ Subscriber stopped");
    }

    void ReadMessage(byte[] bytes) {
        string gesture = System.Text.Encoding.ASCII.GetString(bytes);
        Debug.Log("Received gesture: " + gesture);
        
        // Notify any subscribers about the received gesture
        OnGestureReceived?.Invoke(gesture);
    }
}
