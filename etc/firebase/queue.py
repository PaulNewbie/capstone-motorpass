# firebase/queue.py - Offline Queue Manager

import json
import os
import threading
import time
from datetime import datetime
from etc.firebase.config import SYNC_QUEUE_FILE, CONNECTION_CHECK_INTERVAL, MAX_QUEUE_SIZE, COLLECTIONS

class QueueManager:
    """Manages offline sync queue"""
    
    def __init__(self):
        self.queue = []
        self.running = False
        self.sync_thread = None
        self.get_firebase_db = None
        
        # Load any existing queue
        self._load_queue()
    
    def _load_queue(self):
        """Load queue from file"""
        try:
            if os.path.exists(SYNC_QUEUE_FILE):
                with open(SYNC_QUEUE_FILE, 'r') as f:
                    self.queue = json.load(f)
                print(f"📥 Loaded {len(self.queue)} queued sync items")
        except Exception as e:
            print(f"⚠️  Could not load sync queue: {e}")
            self.queue = []
    
    def _save_queue(self):
        """Save queue to file"""
        try:
            with open(SYNC_QUEUE_FILE, 'w') as f:
                json.dump(self.queue, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save sync queue: {e}")
    
    def add_to_queue(self, collection, document_id, data):
        """Add item to sync queue"""
        try:
            queue_item = {
                'collection': collection,
                'document_id': str(document_id),
                'data': dict(data),
                'queued_at': datetime.now().isoformat(),
                'attempts': 0
            }
            
            self.queue.append(queue_item)
            
            # Limit queue size
            if len(self.queue) > MAX_QUEUE_SIZE:
                self.queue = self.queue[-MAX_QUEUE_SIZE:]
                print(f"⚠️  Queue trimmed to {MAX_QUEUE_SIZE} items")
            
            self._save_queue()
            print(f"📋 Queued for sync: {collection}/{document_id}")
            
        except Exception as e:
            print(f"❌ Error adding to queue: {e}")
    
    def get_queue_size(self):
        """Get current queue size"""
        return len(self.queue)
    
    def process_queue(self, firebase_db):
        """Process all items in queue"""
        if not firebase_db or not self.queue:
            return False
        
        print(f"🔄 Processing {len(self.queue)} queued items...")
        
        try:
            # Import firestore here to avoid circular import
            from firebase_admin import firestore
            
            processed = 0
            failed_items = []
            
            for item in self.queue:
                try:
                    collection = item['collection']
                    document_id = item['document_id']
                    data = item['data']
                    
                    # Add sync timestamp
                    data['synced_at'] = firestore.SERVER_TIMESTAMP
                    
                    # Save to Firebase
                    firebase_db.collection(COLLECTIONS[collection]).document(document_id).set(data, merge=True)
                    
                    processed += 1
                    print(f"✅ Synced: {collection}/{document_id}")
                    
                except Exception as e:
                    print(f"⚠️  Failed to sync {item.get('collection', 'unknown')}/{item.get('document_id', 'unknown')}: {e}")
                    item['attempts'] = item.get('attempts', 0) + 1
                    
                    # Keep failed items if attempts < 3
                    if item['attempts'] < 3:
                        failed_items.append(item)
            
            # Update queue with failed items only
            self.queue = failed_items
            self._save_queue()
            
            if processed > 0:
                print(f"🎉 Successfully synced {processed} items to Firebase")
            
            if failed_items:
                print(f"⚠️  {len(failed_items)} items still pending (will retry)")
            
            return processed > 0
            
        except Exception as e:
            print(f"❌ Error processing queue: {e}")
            return False
    
    def _background_sync_worker(self):
        """Background worker that processes queue when online"""
        while self.running:
            try:
                if self.get_firebase_db and self.queue:
                    firebase_db = self.get_firebase_db()
                    if firebase_db:
                        self.process_queue(firebase_db)
                
                # Wait before next check
                time.sleep(CONNECTION_CHECK_INTERVAL)
                
            except Exception as e:
                print(f"⚠️  Background sync error: {e}")
                time.sleep(5)
    
    def start_background_sync(self, firebase_db_getter):
        """Start background sync worker"""
        if self.running:
            return
        
        self.get_firebase_db = firebase_db_getter
        self.running = True
        self.sync_thread = threading.Thread(target=self._background_sync_worker, daemon=True)
        self.sync_thread.start()
        print("🔄 Background sync worker started")
    
    def stop_background_sync(self):
        """Stop background sync worker"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
        print("🛑 Background sync worker stopped")
    
    def clear_queue(self):
        """Clear all items from queue"""
        self.queue = []
        self._save_queue()
        print("🗑️  Sync queue cleared")

# Global queue manager instance
queue_manager = QueueManager()
