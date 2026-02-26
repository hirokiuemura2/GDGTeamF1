import Ionicons from '@expo/vector-icons/Ionicons';
import { useState } from "react";
import { FlatList, Modal, Pressable, StyleSheet, Text, TextInput, View } from "react-native";


// Mock data
const CATEGORY = [
  { id: 1, title: 'Transport', amount: 'Total' },
  { id: 2, title: 'Food', amount: 'Total' },
  { id: 3, title: 'Shopping', amount: 'Total' },
  { id: 4, title: 'Housing', amount: 'Total' },
  { id: 5, title: 'Health', amount: 'Total' },
]
// Components // Might be wise to move to a different file altogether
const Item = ({ id, title, amount, expose, handleDeleteCategory }: { id: number, title: string, amount: string, expose: boolean, handleDeleteCategory: (id: number) => void}) => (
  <Pressable
    onPress={() => { if (!expose) { console.log("child pressed") } }}
  >
    <View
      style={styles.item}>
      {expose &&
        <Pressable
          style={styles.removeButton}
          onPress={() => handleDeleteCategory(id)
            
          }>
          <Ionicons name="remove-circle" size={30} color="#a90000c1" />
        </Pressable>
      }
      <Text>{title}</Text>
      <Text>{amount}</Text>
    </View>
  </Pressable>
)

export default function Index() {
  // States
  const [categories, setCategories] = useState(CATEGORY)
  const [exposeMenu, setExposeMenu] = useState(false)
  const [modalVisible, setModal] = useState(false)
  const [newCategoryName, setNewCategoryName] = useState("")

  // Helper functions
  const handleCreateCategory = () => {
    if (!newCategoryName.trim()) return
    console.log("New category:", newCategoryName)
    setCategories(prev => [...prev, {
      id: prev.length > 0 ? prev[prev.length - 1].id + 1 : 1,
      title: newCategoryName,
      amount: 'Total'
    }])
    setNewCategoryName("")
    setModal(false)
  }
  
  const handleDeleteCategory = (id: number) => {
    console.log("Category with id deleted: ", id,)
    setCategories(prev => prev.filter(category => category.id !== id))
  }

  return (
    <Pressable
      style={styles.container}
      onLongPress={() => {
        console.log("parent press")
        setExposeMenu(prev => !prev)
      }}
    >
      <View>
        <FlatList data={categories}
          renderItem={({ item }) => <Item id={item.id} title={item.title} amount={item.amount} expose={exposeMenu} handleDeleteCategory={handleDeleteCategory} />}
          keyExtractor={item => item.id.toString()}
          numColumns={3}
          columnWrapperStyle={styles.row}
        />
      </View>

      <Modal
        visible={modalVisible}
        transparent={true}
      >
        <Pressable
          onPress={() => setModal(false)}
          style={styles.modalOverlay}>
          <Pressable style={styles.modalContent} onPress={() => {}}>
            <Text style={styles.modalTitle}>New Category</Text>
            <TextInput
              style={styles.input}
              placeholder="Category name"
              value={newCategoryName}
              onChangeText={setNewCategoryName}
              autoFocus
            />
            <Pressable
              style={styles.submitButton}
              onPress={handleCreateCategory}
            >
              <Text style={styles.submitButtonText}>Create</Text>
            </Pressable>
          </Pressable>
        </Pressable>
      </Modal>

      <Pressable
        style={styles.addButton}
        onPress={() => setModal(prev => !prev)}>
        <Ionicons name="add-circle-sharp" size={60} color="#6495ed" />
      </Pressable>
    </Pressable>
  )
}
const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    backgroundColor: "#ffffff",
    paddingVertical: 20,
    flex: 1,
  },
  row: {
    marginBottom: 10,
    gap: 10,
    justifyContent: "flex-start",
  },
  item: {
    width: 120,
    height: 200,
    gap: 30,
    justifyContent: "flex-end",
    alignItems: "center",
    padding: 5,
    borderRadius: 10,
    backgroundColor: "#6495ed",

  },
  removeButton: {
    position: "absolute",
    top: 0,
    right: 0
  },
  addButton: {
    position: "absolute",
    bottom: 20,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)", // Dim background
    justifyContent: "center",
    alignItems: "center",
  },
  modalContent: {
    backgroundColor: "#ffffff",
    padding: 20,
    borderRadius: 10,
    width: "80%",
    gap: 12,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 4,
  },
  input: {
    borderWidth: 1,
    borderColor: "#d0d0d0",
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
  },
  submitButton: {
    backgroundColor: "#6495ed",
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  submitButtonText: {
    color: "#ffffff",
    fontWeight: "600",
    fontSize: 16,
  }
})
