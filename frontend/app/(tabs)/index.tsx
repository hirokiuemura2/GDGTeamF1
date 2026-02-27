import Ionicons from '@expo/vector-icons/Ionicons';
import { useState } from "react";
import { FlatList, Modal, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { Category, Transaction } from '../../lib/types/transaction.types';


// Mock data
const CATEGORY: Category[] = [
  { id: 1, title: 'Transport', amount: 0 },
  { id: 2, title: 'Food', amount: 0 },
  { id: 3, title: 'Shopping', amount: 0 },
  { id: 4, title: 'Housing', amount: 0 },
  { id: 5, title: 'Health', amount: 0 },
]

const TRANSACTIONS: Transaction[] = [
  { id: 1, currency: 'USD', amount: 100, category: 'Food', description: 'Ate at Mcdonalds', occurred_at: Date() }
]
// Components // Might be wise to move to a different file altogether | sry for the long af function call lol.
const Item = ({ id, title, amount, exposeMenu, setModalTra, handleDeleteCategory }: { id: number, title: string, amount: number, exposeMenu: boolean, setModalTra: (value: boolean) => void, handleDeleteCategory: (id: number) => void }) => (
  <Pressable
    onPress={() => {
      if (!exposeMenu) {
        console.log("child pressed")
        setModalTra(true)
      }
    }
    }
  >
    <View
      style={styles.item}>
      {exposeMenu &&
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
  const [modalCatVisible, setModalCat] = useState(false)
  const [newCategoryName, setNewCategoryName] = useState("")
  const [modalTraVisible, setModalTra] = useState(false)

  // Helper functions
  const handleCreateCategory = () => {
    if (!newCategoryName.trim()) return
    console.log("New category:", newCategoryName)
    setCategories(prev => [...prev, {
      id: prev.length > 0 ? prev[prev.length - 1].id + 1 : 1,
      title: newCategoryName,
      amount: 0
    }])
    setNewCategoryName("")
    setModalCat(false)
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

      {/* Category list and its inside logic, modal etc... */}

      <View>
        <FlatList data={categories}
          renderItem={({ item }) => <Item id={item.id} title={item.title} amount={item.amount} exposeMenu={exposeMenu} handleDeleteCategory={handleDeleteCategory} setModalTra={setModalTra} />}
          keyExtractor={item => item.id.toString()}
          numColumns={3}
          columnWrapperStyle={styles.row}
        />
      </View>
      <Modal
        visible={modalTraVisible}
        transparent={true}
        animationType='slide'
        onRequestClose={() => setModalTra(false)}
      >
        <Pressable
          style={styles.modalTraOverlay}
          onPress={() => setModalTra(false)}
        >
          <View
            style={styles.modalTraContent}>
            <Text>
              hello
            </Text>
          </View>
        </Pressable>
      </Modal>

      {/* Modal and button for creating a new category */}
      <Modal
        visible={modalCatVisible}
        transparent={true}
        onRequestClose={() => setModalCat(false)}
      >
        <Pressable
          onPress={() => setModalCat(false)}
          style={styles.modalCatOverlay}>
          <Pressable style={styles.modalCatContent} onPress={() => { }}>
            <Text style={styles.modalCatTitle}>New Category</Text>
            <TextInput
              style={styles.catInput}
              placeholder="Category name"
              value={newCategoryName}
              onChangeText={setNewCategoryName}
              autoFocus
            />
            <Pressable
              style={styles.submitCatButton}
              onPress={handleCreateCategory}
            >
              <Text style={styles.submitCatButtonText}>Create</Text>
            </Pressable>
          </Pressable>
        </Pressable>
      </Modal>

      <Pressable
        style={styles.addButton}
        onPress={() => setModalCat(prev => !prev)}>
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
  modalCatOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)", // Dim background
    justifyContent: "center",
    alignItems: "center",
  },
  modalCatContent: {
    backgroundColor: "#ffffff",
    padding: 20,
    borderRadius: 10,
    width: "80%",
    gap: 12,
  },
  modalCatTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 4,
  },
  catInput: {
    borderWidth: 1,
    borderColor: "#d0d0d0",
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
  },
  submitCatButton: {
    backgroundColor: "#6495ed",
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  submitCatButtonText: {
    color: "#ffffff",
    fontWeight: "600",
    fontSize: 16,
  },
  modalTraOverlay: {
    flex: 1,
    justifyContent: "flex-end",
    marginVertical: 20,
    marginHorizontal: 10,
  },
  modalTraContent: {
    backgroundColor: "#969696",
    padding: 30,
    borderRadius: 50,
    width: "100%",
    flex: 1,
  }
})
