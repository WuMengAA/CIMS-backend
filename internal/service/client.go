package service

import (
	"errors"
	"time"

	"github.com/MINIOpenSource/CIMS-backend/internal/data"
	"github.com/MINIOpenSource/CIMS-backend/internal/model"
)

var (
	ErrClientNotFound = errors.New("client not found")
)

type ClientService struct{}

func NewClientService() *ClientService {
	return &ClientService{}
}

// Register registers a new client or updates an existing one
func (s *ClientService) Register(uid, name string) error {
	var client model.Client
	result := data.DB.First(&client, "id = ?", uid)

	if result.Error == nil {
		// Update existing
		client.Name = name
		client.UpdatedAt = time.Now()
		return data.DB.Save(&client).Error
	}

	// Create new
	client = model.Client{
		ID:        uid,
		Name:      name,
		Status:    "unknown",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Check pre-registers
	var preReg model.PreRegister
	if err := data.DB.First(&preReg, "id = ?", uid).Error; err == nil {
		// Apply pre-register config
		profile := model.ClientProfile{
			ClientID:        uid,
			ClassPlan:       preReg.ClassPlan,
			TimeLayout:      preReg.TimeLayout,
			Subjects:        preReg.Subjects,
			DefaultSettings: preReg.DefaultSettings,
			Policy:          preReg.Policy,
			UpdatedAt:       time.Now(),
		}
		// Upsert profile
		data.DB.Save(&profile)
		// Remove pre-register
		data.DB.Delete(&preReg)
	}

	return data.DB.Create(&client).Error
}

func (s *ClientService) UnRegister(uid string) error {
	tx := data.DB.Begin()
	if err := tx.Delete(&model.Client{}, "id = ?", uid).Error; err != nil {
		tx.Rollback()
		return err
	}
	if err := tx.Delete(&model.ClientProfile{}, "client_id = ?", uid).Error; err != nil {
		tx.Rollback()
		return err
	}
	return tx.Commit().Error
}

func (s *ClientService) UpdateHeartbeat(uid, ip string) error {
	return data.DB.Model(&model.Client{}).Where("id = ?", uid).Updates(map[string]interface{}{
		"status":         "online",
		"ip":             ip,
		"last_heartbeat": time.Now(),
	}).Error
}

func (s *ClientService) GetClient(uid string) (*model.Client, error) {
	var client model.Client
	if err := data.DB.First(&client, "id = ?", uid).Error; err != nil {
		return nil, err
	}
	return &client, nil
}

func (s *ClientService) GetAllClients() ([]model.Client, error) {
	var clients []model.Client
	if err := data.DB.Find(&clients).Error; err != nil {
		return nil, err
	}
	return clients, nil
}
