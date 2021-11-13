using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using System;
using System.IO;

using System.Net;
using System.Net.Sockets;
using System.Runtime.InteropServices;

using System.Text;

public class UnitySocket : MonoBehaviour
{
    TcpClient client;
    public string serverIP = "localhost"; //"127.0.0.1";
    public int port = 8081; //60000;

    byte[] receivedBuffer;
    StreamReader reader;
    bool socketReady = false;
    NetworkStream stream;

    byte[] bufLength;
    byte[] bufData;
    byte[] bufTime;

    string dataLength;
    string stringData;
    string sTime;

    // Start is called before the first frame update
    void Start()
    {
        //check receive
        if (socketReady)
        {
            return;
        }

        try
        {
            client = new TcpClient(serverIP, port);
            if (client.Connected)
            {
                stream = client.GetStream();
                Debug.Log("Connect Success");
                socketReady = true;
            }
        }
        catch (Exception e)
        {
            Debug.Log("On client connect exception " + e);
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (socketReady)
        {
            if (stream.DataAvailable)
            {
                receivedBuffer = new byte[64];
                stream.Read(receivedBuffer, 0, receivedBuffer.Length);
                //stream.
                sTime = Encoding.UTF8.GetString(receivedBuffer, 0, receivedBuffer.Length);
                Debug.Log(sTime);

                //stream.Write();
                /*
                bufLength = new byte[64];
                stream.Read(bufLength, 0, bufLength.Length);
                dataLength = Encoding.UTF8.GetString(bufLength, 0, bufLength.Length);
                
                bufData = new byte[int.Parse(dataLength)];
                stream.Read(bufData, 0, bufData.Length);
                stringData = Encoding.UTF8.GetString(bufData, 0, bufData.Length);

                bufTime = new byte[64];
                stream.Read(bufTime, 0, bufTime.Length);
                sTime = Encoding.UTF8.GetString(bufData, 0, bufData.Length);

                // byte[] to string: GetString(byte [] bytes, int index, int count)
                //string msg = Encoding.UTF8.GetString(receivedBuffer, 0, receivedBuffer.Length);
                */

                /*
                 *  byte[] bytes = Encoding.Default.GetBytes(myString);
                 *  myString = Encoding.UTF8.GetString(bytes);
                */
                //Debug.Log(stringData);
                //Debug.Log(sTime);
            }
        }
    }

    

    void OnApplicationQuit()
    {
        // CloseSocket
        if (!socketReady)
        {
            return;
        }

        reader.Close();
        client.Close();
        socketReady = false;

    }
}
