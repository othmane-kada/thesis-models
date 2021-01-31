/**
 * Module provides tandem model components.
 *
 * Defines these models:
 *
 * - Packet: represents packets transmitted between nodes
 * - Queue: represents a FIFO buffer, finite or infinite
 * - Server: models a server with (random) service time
 * - Source: models a packets source
 * - Node: models a network node, that contains queue, server and source (opt.)
 * - Network: a collection of nodes
 *
 * Note, that the packet_ is treated delivered _after_ service end at the
 * destination node.
 *
 * @author Andrey Larionov
 */
#ifndef CQUMO_TANDEM_COMPONENTS_H
#define CQUMO_TANDEM_COMPONENTS_H

#include "Base.h"
#include "Journals.h"
#include "Functions.h"
#include <queue>
#include <functional>
#include <map>


namespace cqumo {

class Node;


/**
 * Class representing packets generated by sources and transmitted
 * between nodes. Fields source, target and createdAt are immutable.
 * Also contains fields for tracking packet_ transmission, which can be
 * re-written during the packet_ processing.
 */
class Packet : public Object {
  public:
    /**
     * Constructor.
     * @param source source node address
     * @param target target node address
     * @param createdAt model time when the packet_ was created
     */
    Packet(int source, int target, double createdAt);

    ~Packet() override = default;

    /** Get source node address. */
    inline int source() const { return source_; }

    /** Get target node address. */
    inline int target() const { return target_; }

    /** Get model time when the packet_ was created. */
    inline double createdAt() const { return createdAt_; }

    /** Get model time when the packet_ arrived at current node. */
    inline double arrivedAt() const { return arrivedAt_; }

    /** Set model time when the packet_ arrived at current node. */
    inline void setArrivedAt(double time) { arrivedAt_ = time; }

    /** Get string representation of the packet_. */
    std::string toString() const override;

  private:
    int source_;
    int target_;
    double createdAt_;
    double arrivedAt_ = 0.0;
};


/**
 * Base class for objects stored inside Node.
 * Provides owner (Node) getter and setter.
 */
class NodeComponent : public Object {
  public:
    NodeComponent() = default;
    ~NodeComponent() override = default;

    /** Get owning Node. */
    inline Node *owner() const { return owner_; }

    /** Set owning Node. */
    inline void setOwner(Node *node) { this->owner_ = node; }

    /** Helper to value owning node address. */
    int address() const;

  private:
    Node *owner_ = nullptr;
};


/**
 * FIFO queue with finite or infinite capacity_.
 * Queue stores packets. When the Queue is destroyed,
 * all packets contained inside it are also destroyed.
 */
class Queue : public NodeComponent {
  public:
    /**
     * Create a queue.
     * @param capacity if negative, queue is treated infinite (default).
     *      Otherwise, specifies the maximum number of packets those can
     *      be stored in the queue.
     */
    explicit Queue(int capacity = -1);

    /** Destroy the queue and all stored packets. */
    ~Queue() override;

    /**
     * Put a packet_ into the queue. If queue is full, do nothing and
     * return 0. Otherwise, return 1.
     * @param packet
     * @return number of packets put into the queue.
     */
    int push(Packet *packet);

    /**
     * Extract the next packet_ from the queue, if not empty. If
     * the queue was empty, return nullptr.
     * @return packet_ or nullptr
     */
    Packet *pop();

    /** Get number of packets in the queue. */
    inline unsigned size() const { return packets_.size(); }

    /** Check whether there are packets in the queue. */
    inline bool empty() { return packets_.empty(); }

    /** Get queue capacity_. */
    inline int capacity() const { return capacity_; }

    /**
     * Check whether the queue is full. For queues with infinite capacity_,
     * always return false.
     */
    inline bool full() const {
        return capacity_ >= 0 && static_cast<int>(packets_.size()) >= capacity_;
    }

    /** Get string representation of the queue. */
    std::string toString() const override;

  protected:
    std::queue<Packet *> packets_;
    int capacity_;
};


/**
 * Model of a server. It is specified with a service interval function.
 * Server can store one packet. Its API is very close to Queue, while
 * ready() and busy() methods are used instead of empty() and full().
 */
class Server : public NodeComponent {
  public:
    /**
     * Create a server.
     * @param intervals a function without arguments to value service intervals
     */
    explicit Server(const DblFn& intervals);

    /** Destroy the server and the packet it is serving. */
    ~Server() override;

    /**
     * Put a packet into the server, if it was empty. If the server was busy,
     * nothing happens and 0 is returned.
     * @param packet
     * @return 1 if server was empty, 0 if not.
     */
    int push(Packet *packet);

    /**
     * Get packet that was under service, or nullptr if server was empty.
     * After calling this method, server becomes ready.
     * @return packet if server was busy, or nullptr otherwise.
     */
    Packet *pop();

    /** Check whether there is a packet under service. */
    inline bool busy() const { return packet_ != nullptr; }

    /** Check whether there is no packet under service. */
    inline bool ready() const { return packet_ == nullptr; }

    /** Get the number of packets under service. */
    inline unsigned size() const { return packet_ ? 1 : 0; }

    /** Get next service interval. */
    inline double interval() const { return intervals_(); }

    /** Get the last model time when the server became empty. */
    inline double lastDepartureAt() const { return lastDepartureAt_; }

    /** Store the model time when the server became empty. */
    inline void setLastDepartureAt(double time) { lastDepartureAt_ = time; }

    /** Get string representation of the server object. */
    std::string toString() const override;

  private:
    DblFn intervals_;
    Packet *packet_ = nullptr;
    double lastDepartureAt_ = 0.0;
};


/**
 * Model of traffic source. Generates packets to a given destination with
 * specified intervals distribution.
 */
class Source : public NodeComponent {
  public:
    /**
     * Create source.
     * @param intervals a function without arguments to value arrival intervals
     * @param target destination node address
     */
    explicit Source(const DblFn& intervals, int target);

    ~Source() override = default;

    /** Get next arrival interval. */
    inline double interval() const { return intervals_(); }

    /** Get packet destination address. */
    inline int target() const { return target_; }

    /** Create new packet. */
    Packet *createPacket(double time) const;

    /** Get string representation. */
    std::string toString() const override;

  private:
    DblFn intervals_;
    int target_;
};


/**
 * Model of a network node. It contains an address, Server, Queue and
 * optionally Source. Node can be connected to another node where it
 * forwards packets.
 */
class Node : public Object {
  public:
    /**
     * Create node.
     * @param address integer address
     * @param queue  queue component, mandatory
     * @param server server component, mandatory
     * @param source optional source (default: nullptr)
     */
    Node(int address, Queue *queue, Server *server, Source *source = nullptr);

    /** Destroy the node along with its internal queue, server, source. */
    ~Node() override;

    /** Get node address. */
    inline int address() const { return address_; }

    /** Get queue component. */
    inline Queue *queue() const { return queue_; }

    /** Get server component. */
    inline Server *server() const { return server_; }

    /** Get source component. */
    inline Source *source() const { return source_; }

    /** Set next node - neighbour the node forwards served packets to. */
    inline void setNextHop(Node *node) { nextHop_ = node; }

    /** Get next node. */
    inline Node *nextHop() const { return nextHop_; }

    /** Get node size - sum of queue and server sizes. */
    inline unsigned size() const {
        return queue_->size() + server_->size();
    }

    /** Get string representation. */
    std::string toString() const override;

  private:
    int address_;
    Queue *queue_;
    Server *server_;
    Source *source_;
    Node *nextHop_;
};


/**
 * Network is just a collection of nodes. In current version it allows
 * to add and get nodes by their addresses, or value a collection of all nodes.
 * When the network is destroyed, all nodes in this network are also destroyed.
 */
class Network : public Object {
  public:
    Network() = default;

    /** Destroy network and all its nodes. */
    ~Network() override;

    /**
     * Add a node to the network. If a node with the same address already
     * exists, std::runtime_error exception is thrown.
     */
    void addNode(Node *node);

    /** Get node by address. If not found, returns nullptr. */
    inline Node *node(int address) const {
        auto iter = nodes_.find(address);
        if (iter == nodes_.end()) {
            return nullptr;
        }
        return iter->second;
    }

    /** Get a mapping of all nodes. */
    inline const std::map<int, Node *>& nodes() const { return nodes_; }

    /** Get network string representation. */
    std::string toString() const override;

  private:
    std::map<int, Node *> nodes_;
};


// Helpers
// --------------------------------------------------------------------------
/**
 * Build a network with a single node, that contains source, and that is
 * the packets target (i.e. after serving packets are treated delivered).
 * This kind of network represents a G/G/1 or G/G/1/N system.
 *
 * @param arrival function without arguments returning arrival intervals
 * @param service function without arguments returning service intervals
 * @param queueCapacity if negative, queue is infinite
 * @return Network
 */
Network *buildOneHopeNetwork(
        const DblFn &arrival,
        const DblFn &service,
        int queueCapacity);

}

#endif //CQUMO_TANDEM_COMPONENTS_H
