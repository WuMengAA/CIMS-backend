package data

import (
	"log"
	"os"
	"path/filepath"

	"github.com/MINIOpenSource/CIMS-backend/internal/model"
	"github.com/glebarez/sqlite"
	"gorm.io/gorm"
)

var DB *gorm.DB

// InitDB initializes the SQLite database
func InitDB(dbPath string) error {
	var err error

	dir := filepath.Dir(dbPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	DB, err = gorm.Open(sqlite.Open(dbPath), &gorm.Config{})
	if err != nil {
		return err
	}

	// Migrate new schema
	err = DB.AutoMigrate(
		&model.Client{},
		&model.CPFile{},
		&model.TLFile{},
		&model.SubFile{},
		&model.PolicyFile{},
		&model.SettingsFile{},
		&model.ClientProfile{},
		&model.PreRegister{},
		&model.Setting{}, // System settings
	)
	if err != nil {
		return err
	}

	log.Println("Database initialized at", dbPath)
	return nil
}
