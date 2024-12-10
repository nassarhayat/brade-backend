// @ts-check
import fs from "fs"
import express from "express"
import { WebSocketServer } from "ws"
import { Repo } from "@automerge/automerge-repo"
import { NodeWSServerAdapter } from "@automerge/automerge-repo-network-websocket"
import { NodeFSStorageAdapter } from "@automerge/automerge-repo-storage-nodefs"
import os from "os"

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000'

async function updateDocumentIndex(documentId, content) {
  try {
    // Format the document data according to the DocumentIndex model requirements
    const documentData = {
      title: content?.content?.title || "Untitled",
      content: JSON.stringify(content), // Store the full content as a JSON string
      document_type: content?.content?.type || "document",
      tags: content?.content?.tags || [],
      author: content?.content?.author,
      source_url: content?.content?.source_url,
      summary: content?.content?.summary
    };
    
    const response = await fetch(`${FASTAPI_URL}/documents_index/${documentId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(documentData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log("Document index updated successfully:", result);
    return result;
  } catch (error) {
    console.error("Failed to update document index:", error);
    // Instead of throwing, return an error object
    return {
      type: 'error',
      message: error.message
    };
  }
}

export class Server {
  /** @type WebSocketServer */
  #socket

  /** @type WebSocketServer */
  #apiSocket

  /** @type ReturnType<import("express").Express["listen"]> */
  #server

  /** @type {((value: any) => void)[]} */
  #readyResolvers = []

  #isReady = false

  /** @type Repo */
  #repo

  constructor() {
    const dir =
      process.env.DATA_DIR !== undefined ? process.env.DATA_DIR : ".amrg"
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir)
    }

    var hostname = os.hostname()

    // Initialize both WebSocket servers first
    this.#socket = new WebSocketServer({ noServer: true })
    this.#apiSocket = new WebSocketServer({ noServer: true })

    const PORT = process.env.PORT || 3030
    const app = express()
    app.use(express.static("public"))

    const config = {
      network: [new NodeWSServerAdapter(this.#socket)],
      storage: new NodeFSStorageAdapter(dir),
      /** @ts-ignore @type {(import("@automerge/automerge-repo").PeerId)}  */
      peerId: `storage-server-${hostname}`,
      sharePolicy: async () => true,
    }
    this.#repo = new Repo(config)

    app.get("/", (req, res) => {
      res.send(`👍 @automerge/automerge-repo-sync-server is running`)
    })

    this.#server = app.listen(PORT, () => {
      console.log(`Listening on port ${PORT}`)
      this.#isReady = true
      this.#readyResolvers.forEach((resolve) => resolve(true))
    })

    // Set up upgrade handler after both WebSocket servers are initialized
    this.#server.on("upgrade", (request, socket, head) => {
      if (request.url === "/" || request.url === "/automerge") {
        this.#socket.handleUpgrade(request, socket, head, (ws) => {
          this.#socket.emit("connection", ws, request)
        })
      } else if (request.url === "/api") {
        this.#apiSocket.handleUpgrade(request, socket, head, (ws) => {
          this.#apiSocket.emit("connection", ws, request)
        })
      } else {
        socket.destroy()
      }
    })

    // Set up API WebSocket handlers
    this.#apiSocket.on("connection", (ws) => {
      console.log("New API WebSocket connection established")

      ws.on("message", async (message) => {
        try {
          const data = JSON.parse(message.toString())
          console.log("Received API message:", data)

          let response

          switch (data.type) {
            case "get_document": {
              let doc = null;
              try {
                if (data.documentId) {
                  doc = this.#repo.find(data.documentId);
                }
              } catch (e) {
                console.error("Error finding document:", e);
              }

              if (doc) {
                const docContent = await doc.doc();
                response = {
                  type: "document",
                  documentId: data.documentId,
                  content: docContent || null
                };
              } else {
                response = {
                  type: "document",
                  documentId: data.documentId,
                  content: null,
                };
              }
              break;
            }

            case "update_document": {
              let doc;
              let documentId = data.documentId;

              console.log("Updating document:", documentId)

              try {
                if (documentId) {
                  doc = this.#repo.find(documentId);
                } else {
                  doc = this.#repo.create();
                  documentId = doc.documentId;
                }

                console.log("Document found:", doc)

                doc.change((d) => {
                  // Initialize document if needed
                  if (!d.content) d.content = {};
                  if (!d.metadata) d.metadata = {};

                  // Simply mirror the incoming content structure
                  for (const [key, value] of Object.entries(data.content)) {
                    d[key] = value;
                  }
                });
                
                response = {
                  type: "success",
                  documentId: documentId
                };
              } catch (e) {
                console.error("Error updating document:", e);
                response = {
                  type: "error",
                  message: e.message
                };
              }
              break;
            }

            default:
              response = {
                type: "error",
                message: "Unknown message type",
              }
          }

          console.log("Sending API response:", response)
          ws.send(JSON.stringify(response))
        } catch (error) {
          console.error("Error processing API message:", error)
          ws.send(
            JSON.stringify({
              type: "error",
              message: error.message,
            })
          )
        }
      })

      ws.on("error", (error) => {
        console.error("WebSocket API error:", error)
      })

      ws.on("close", () => {
        console.log("WebSocket API connection closed")
      })
    })
  }

  async ready() {
    if (this.#isReady) {
      return true
    }

    return new Promise((resolve) => {
      this.#readyResolvers.push(resolve)
    })
  }

  close() {
    this.#socket.close()
    this.#server.close()
  }
}

const server = new Server()
